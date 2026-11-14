# main.py - MiniDrone flight controller for ESP32-S3 Mini boards (MicroPython)
#
# The ESP32-S3 creates its own WiFi network. Connect your phone to it and open
# http://192.168.4.1 in the browser to get the joystick controller.
#
# Upload to the board: main.py, mpu6050.py, gyroscope.py
#
# !!! TEST WITH PROPELLERS REMOVED FIRST !!!

import network
import asyncio
import time
import math
import struct
import hashlib
import binascii
import gc
from machine import Pin, PWM, I2C
from mpu6050 import MPU6050
from gyroscope import print_gyro_help

# ============================ CONFIG ============================
WIFI_SSID = "MiniDrone"
WIFI_PASS = "flyhigh123"            # at least 8 characters

# ESP32 S3 Mini (silkscreen D1,D2,D3,D8 / D4,D5 for I2C)
I2C_SDA, I2C_SCL = 5, 6               # D4 = SDA, D5 = SCL
I2C_PIN_FALLBACKS = ((5, 6), (8, 9))  # try D4/D5 first, then common alternate

# Motors: front-left, front-right, rear-left, rear-right
MOTOR_PINS = (2, 3, 4, 7)             # D1, D2, D3, D8
# Avoid GPIO 0, 3, 45, 46 (boot), 19/20 (USB), 26-37 (flash/PSRAM).

# Status LED: set to your board's LED pin, or None to disable.
LED_PIN = None
LED_IS_RGB = False
# 1000 Hz suits MX1508 / DRV8833 PWM inputs; 20000 Hz for tiny coreless motors direct on GPIO
PWM_FREQ = 1000

LOOP_HZ = 250
ALPHA = 0.98                        # complementary filter: trust in gyro

MAX_ANGLE = 25.0                    # deg of tilt at full stick
MAX_YAW_RATE = 150.0                # deg/s at full stick
ANGLE_KP = 4.0                      # angle error (deg) -> rate target (deg/s)

# Rate PID gains (kp, ki, kd). Output is a fraction of full motor power.
ROLL_PID = (0.0012, 0.0030, 0.00002)
PITCH_PID = (0.0012, 0.0030, 0.00002)
YAW_PID = (0.0030, 0.0020, 0.0)
I_LIMIT = 0.15
OUT_LIMIT = 0.35

IDLE = 0.08                         # motor power when armed at zero throttle
FAILSAFE_MS = 500                   # cut motors if phone goes silent this long
TILT_CUTOFF = 60.0                  # deg: assume crash, cut motors
# ================================================================


class StatusLed:
    def __init__(self, pin, rgb):
        self.np = self.pin = None
        if pin is None:
            return
        if rgb:
            try:
                import neopixel
                self.np = neopixel.NeoPixel(Pin(pin, Pin.OUT), 1)
            except ImportError:
                print("No neopixel module; LED disabled")
        else:
            self.pin = Pin(pin, Pin.OUT)
        self.off()

    def _set(self, on, color):
        if self.np:
            self.np[0] = color if on else (0, 0, 0)
            self.np.write()
        elif self.pin:
            self.pin.value(on)

    def on(self, color=(40, 0, 0)):      # red = armed
        self._set(1, color)

    def off(self):
        self._set(0, None)


led = StatusLed(LED_PIN, LED_IS_RGB)

# ---------- motors ----------
motors = []
for p in MOTOR_PINS:
    m = PWM(Pin(p))
    m.freq(PWM_FREQ)
    m.duty_u16(0)
    motors.append(m)


def set_motors(vals):
    for m, v in zip(motors, vals):
        if v < 0.0:
            v = 0.0
        elif v > 1.0:
            v = 1.0
        m.duty_u16(int(v * 65535))


set_motors((0, 0, 0, 0))


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


# ---------- PID ----------
class PID:
    def __init__(self, gains):
        self.kp, self.ki, self.kd = gains
        self.reset()

    def reset(self):
        self.i = 0.0
        self.prev = 0.0
        self.d = 0.0

    def update(self, err, dt, integrate):
        if integrate:
            self.i = clamp(self.i + err * self.ki * dt, -I_LIMIT, I_LIMIT)
        raw_d = (err - self.prev) / dt
        self.prev = err
        self.d += 0.3 * (raw_d - self.d)          # low-pass the D term
        return clamp(self.kp * err + self.i + self.kd * self.d,
                     -OUT_LIMIT, OUT_LIMIT)


pid_roll = PID(ROLL_PID)
pid_pitch = PID(PITCH_PID)
pid_yaw = PID(YAW_PID)


# ---------- mixer (X configuration, props-in) ----------
def mix(base, r, p, y):
    m = [base + r - p + y,   # FL
         base - r - p - y,   # FR
         base + r + p - y,   # RL
         base - r + p + y]   # RR
    hi = max(m)
    if hi > 1.0:
        m = [v - (hi - 1.0) for v in m]
    return [clamp(v, IDLE, 1.0) for v in m]


# ---------- shared state ----------
cmd = {"thr": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0,
       "arm": False, "t": time.ticks_ms()}
tel = {"armed": False, "roll": 0.0, "pitch": 0.0, "reason": ""}
arm_block = False


def disarm(reason=""):
    global arm_block
    tel["armed"] = False
    set_motors((0, 0, 0, 0))
    led.off()
    if reason:
        arm_block = True
        tel["reason"] = reason
        print("DISARMED:", reason)


# ---------- flight loop ----------
async def flight_loop(imu):
    global arm_block
    ax, ay, az, _, _, _ = imu.read()
    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))

    period = 1_000_000 // LOOP_HZ
    last = time.ticks_us()

    while True:
        now = time.ticks_us()
        el = time.ticks_diff(now, last)
        if el < period:
            await asyncio.sleep_ms(1 if period - el > 1500 else 0)
            continue
        last = now
        dt = min(el * 1e-6, 0.02)

        try:
            ax, ay, az, gx, gy, gz = imu.read()
        except OSError:
            disarm("IMU read error")
            continue

        acc_roll = math.degrees(math.atan2(ay, az))
        acc_pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
        roll = ALPHA * (roll + gx * dt) + (1 - ALPHA) * acc_roll
        pitch = ALPHA * (pitch + gy * dt) + (1 - ALPHA) * acc_pitch
        tel["roll"] = roll
        tel["pitch"] = pitch

        link_ok = time.ticks_diff(time.ticks_ms(), cmd["t"]) < FAILSAFE_MS
        armed = tel["armed"]

        if armed and not link_ok:
            disarm("signal lost")
            continue
        if armed and (abs(roll) > TILT_CUTOFF or abs(pitch) > TILT_CUTOFF):
            disarm("tilted over")
            continue

        if not cmd["arm"]:
            arm_block = False
            tel["reason"] = ""
            if armed:
                disarm()
            continue
        if not armed:
            if not arm_block and link_ok and cmd["thr"] < 0.05:
                pid_roll.reset()
                pid_pitch.reset()
                pid_yaw.reset()
                tel["armed"] = True
                led.on()
                print("ARMED")
            else:
                continue

        thr = cmd["thr"]
        roll_rate_sp = ANGLE_KP * (cmd["roll"] * MAX_ANGLE - roll)
        pitch_rate_sp = ANGLE_KP * (cmd["pitch"] * MAX_ANGLE - pitch)
        yaw_rate_sp = -cmd["yaw"] * MAX_YAW_RATE

        integrate = thr > 0.15
        u_r = pid_roll.update(roll_rate_sp - gx, dt, integrate)
        u_p = pid_pitch.update(pitch_rate_sp - gy, dt, integrate)
        u_y = pid_yaw.update(yaw_rate_sp - gz, dt, integrate)

        base = IDLE + thr * (1.0 - IDLE)
        set_motors(mix(base, u_r, u_p, u_y))


# ---------- tiny WebSocket server ----------
WS_GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


async def ws_send(writer, text):
    b = text.encode()
    writer.write(bytes((0x81, len(b))) + b)
    await writer.drain()


async def ws_session(reader, writer, key):
    accept = binascii.b2a_base64(hashlib.sha1(key.encode() + WS_GUID).digest()).strip()
    writer.write(b"HTTP/1.1 101 Switching Protocols\r\n"
                 b"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                 b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n")
    await writer.drain()
    print("Phone connected")
    last_tx = time.ticks_ms()

    while True:
        hdr = await reader.readexactly(2)
        op = hdr[0] & 0x0F
        ln = hdr[1] & 0x7F
        if ln == 126:
            ln = struct.unpack(">H", await reader.readexactly(2))[0]
        elif ln == 127:
            return
        mask = await reader.readexactly(4) if hdr[1] & 0x80 else b"\0\0\0\0"
        data = bytearray(await reader.readexactly(ln))
        for i in range(ln):
            data[i] ^= mask[i & 3]

        if op == 8:
            return
        if op == 1:
            try:
                p = data.decode().split(",")
                cmd["thr"] = clamp(float(p[0]), 0.0, 1.0)
                cmd["roll"] = clamp(float(p[1]), -1.0, 1.0)
                cmd["pitch"] = clamp(float(p[2]), -1.0, 1.0)
                cmd["yaw"] = clamp(float(p[3]), -1.0, 1.0)
                cmd["arm"] = p[4] == "1"
                cmd["t"] = time.ticks_ms()
            except (ValueError, IndexError):
                pass

        if time.ticks_diff(time.ticks_ms(), last_tx) > 200:
            last_tx = time.ticks_ms()
            await ws_send(writer, "%d,%.1f,%.1f,%s" % (
                tel["armed"], tel["roll"], tel["pitch"], tel["reason"]))


async def handle_client(reader, writer):
    try:
        await reader.readline()
        headers = {}
        while True:
            line = await reader.readline()
            if not line or line == b"\r\n":
                break
            k, _, v = line.decode().partition(":")
            headers[k.strip().lower()] = v.strip()

        if headers.get("upgrade", "").lower() == "websocket":
            await ws_session(reader, writer, headers.get("sec-websocket-key", ""))
        else:
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
                         b"Connection: close\r\n\r\n")
            writer.write(HTML)
            await writer.drain()
    except Exception as e:
        print("client error:", e)
    finally:
        writer.close()
        await writer.wait_closed()


HTML = b"""<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>MiniDrone</title><style>
html,body{margin:0;height:100%;background:#1b2430;color:#d8e1ea;
font-family:system-ui,sans-serif;touch-action:none;user-select:none;-webkit-user-select:none}
body{display:flex;flex-direction:column}
#bar{display:flex;justify-content:space-between;align-items:center;padding:10px 14px}
#st{font-size:15px}
#arm{font-size:17px;font-weight:600;padding:10px 22px;border:2px solid #f2a33a;
border-radius:24px;background:transparent;color:#f2a33a}
#arm.on{background:#e5484d;border-color:#e5484d;color:#fff}
#pads{flex:1;display:flex;gap:12px;padding:0 12px 12px}
.pad{flex:1;position:relative;border:2px solid #34465a;border-radius:20px;
background:radial-gradient(circle,#223041 0,#1b2430 70%)}
.pad span{position:absolute;bottom:8px;width:100%;text-align:center;font-size:12px;color:#6f8399}
.knob{position:absolute;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;
background:#f2a33a;box-shadow:0 0 0 6px rgba(242,163,58,.2)}
</style></head><body>
<div id="bar"><span id="st">Connecting</span><button id="arm">Arm</button></div>
<div id="pads">
<div class="pad" id="L"><div class="knob"></div><span>Throttle and yaw</span></div>
<div class="pad" id="R"><div class="knob"></div><span>Pitch and roll</span></div>
</div>
<script>
var S={L:{x:0,y:-1},R:{x:0,y:0}},want=false,ws=null,st=document.getElementById('st'),
btn=document.getElementById('arm');
function pad(id,springY){var el=document.getElementById(id),k=el.querySelector('.knob'),s=S[id],pid=null;
function draw(){k.style.left=(50+s.x*50)+'%';k.style.top=(50-s.y*50)+'%';}
function mv(e){var r=el.getBoundingClientRect();
s.x=Math.max(-1,Math.min(1,(e.clientX-r.left)/r.width*2-1));
s.y=Math.max(-1,Math.min(1,1-(e.clientY-r.top)/r.height*2));draw();}
el.addEventListener('pointerdown',function(e){pid=e.pointerId;el.setPointerCapture(pid);mv(e);});
el.addEventListener('pointermove',function(e){if(e.pointerId===pid)mv(e);});
function up(e){if(e.pointerId!==pid)return;pid=null;s.x=0;if(springY)s.y=0;draw();}
el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);draw();}
pad('L',false);pad('R',true);
function dz(v){return Math.abs(v)<0.06?0:v;}
function ui(){btn.textContent=want?'Disarm':'Arm';btn.className=want?'on':'';}
btn.onclick=function(){want=!want;ui();};
function conn(){ws=new WebSocket('ws://'+location.host+'/ws');
ws.onopen=function(){st.textContent='Connected';};
ws.onclose=function(){st.textContent='No link to drone, retrying';want=false;ui();setTimeout(conn,1000);};
ws.onmessage=function(e){var p=e.data.split(',');
if(want&&p[0]=='0'&&p[3]){want=false;ui();}
st.textContent=(p[0]=='1'?'Armed':(want?'Lower throttle to arm':'Disarmed'))+
' | roll '+p[1]+' pitch '+p[2]+(p[3]?' | '+p[3]:'');};}
conn();
setInterval(function(){if(!ws||ws.readyState!==1)return;
var thr=(S.L.y+1)/2;
ws.send(thr.toFixed(3)+','+dz(S.R.x).toFixed(3)+','+dz(S.R.y).toFixed(3)+','+
dz(S.L.x).toFixed(3)+','+(want?1:0));},50);
</script></body></html>"""


def connect_imu():
    """Open I2C and return MPU6050 wrapper, trying each pin pair."""
    last_scan = []
    for sda, scl in I2C_PIN_FALLBACKS:
        try:
            i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=400000)
            found = i2c.scan()
            last_scan = found
            print("I2C scan SDA=%d SCL=%d:" % (sda, scl), [hex(a) for a in found])
            if 0x68 in found or 0x69 in found:
                return MPU6050(i2c)
        except OSError as e:
            print("I2C error SDA=%d SCL=%d:" % (sda, scl), e)
    print_gyro_help(I2C_SDA, I2C_SCL)
    raise OSError("ENODEV: no MPU6050 (scan=%s)" % ([hex(a) for a in last_scan]))


# ---------- startup ----------
async def main():
    try:
        imu = connect_imu()
    except OSError:
        print("Fix gyro wiring, then reset the board.")
        while True:
            await asyncio.sleep(1)

    print("Calibrating gyro - keep the drone still...")
    if LED_PIN is not None:
        led.on((0, 0, 40))
    imu.calibrate_gyro()
    led.off()

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=WIFI_SSID, password=WIFI_PASS,
              authmode=network.AUTH_WPA2_PSK, max_clients=2)
    while not ap.active():
        await asyncio.sleep_ms(100)
    try:
        ap.config(txpower=15)
    except Exception:
        pass
    ip = ap.ifconfig()[0]
    print("Join WiFi '%s' (password %s) and open http://%s" % (WIFI_SSID, WIFI_PASS, ip))

    await asyncio.start_server(handle_client, "0.0.0.0", 80)
    gc.collect()
    await flight_loop(imu)


try:
    asyncio.run(main())
finally:
    set_motors((0, 0, 0, 0))