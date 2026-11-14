"""
Drone main program — ESP32 S3 Mini (Thonny / MicroPython).

Pin labels D1, D2, … are printed on the edge of the board.
Gyro logic is in gyroscope.py. No potentiometer: see THROTTLE_MANUAL.
"""

import time
from machine import Pin, PWM

from gyroscope import init_gyro, print_gyro_help

# =============================================================================
# PIN ALLOCATION (change only here)
# Board silkscreen → GPIO
# =============================================================================

# Motors FL, FR, RL, RR  —  D1, D2, D3, D8
MOTOR_PINS = (2, 3, 4, 7)

# MPU6050 I2C  —  D4 = SDA, D5 = SCL on many ESP32 S3 Mini boards (GPIO 5 & 6)
GYRO_I2C_ID = 0
GYRO_SDA_PIN = 5
GYRO_SCL_PIN = 6
GYRO_I2C_FREQ = 400_000

# If I2C scan is empty, code tries these pin pairs in order (edit if your board differs)
I2C_PIN_FALLBACKS = (
    (5, 6),   # D4, D5
    (8, 9),   # some ESP32 S3 boards default I2C
)

# Throttle with no potentiometer: 0.0 = motors idle (safe). Raise only for bench tests.
THROTTLE_MANUAL = 0.0

# =============================================================================
# TUNING
# =============================================================================

MOTOR_PWM_HZ = 1000
PWM_MAX = 65535

ROLL_GAIN = 0.6
PITCH_GAIN = 0.6
YAW_GAIN = 0.8

LOOP_DT = 0.02

# =============================================================================
# MOTORS
# =============================================================================

class MotorBank:
    def __init__(self, pins=MOTOR_PINS):
        self._pwms = []
        for p in pins:
            self._pwms.append(PWM(Pin(p), freq=MOTOR_PWM_HZ, duty_u16=0))

    def off(self):
        self.set_four(0, 0, 0, 0)

    def set_four(self, fl, fr, rl, rr):
        for i, level in enumerate((fl, fr, rl, rr)):
            level = max(0.0, min(1.0, level))
            duty = 0 if level <= 0 else int(level * PWM_MAX)
            self._pwms[i].duty_u16(duty)


# =============================================================================
# THROTTLE & MIXER
# =============================================================================


def read_throttle():
    t = THROTTLE_MANUAL
    if t < 0.0:
        return 0.0
    if t > 1.0:
        return 1.0
    return t


def mix_motors(base, gx, gy, gz):
    roll = gx * ROLL_GAIN / 100.0
    pitch = gy * PITCH_GAIN / 100.0
    yaw = gz * YAW_GAIN / 100.0

    fl = base + pitch + roll - yaw
    fr = base + pitch - roll + yaw
    rl = base - pitch + roll + yaw
    rr = base - pitch - roll - yaw

    def clamp(v):
        return max(0.0, min(1.0, v))

    return clamp(fl), clamp(fr), clamp(rl), clamp(rr)


# =============================================================================
# RUN
# =============================================================================


def connect_gyro():
    last_err = None
    for sda, scl in I2C_PIN_FALLBACKS:
        try:
            return init_gyro(sda, scl, GYRO_I2C_ID, GYRO_I2C_FREQ), sda, scl
        except OSError as e:
            last_err = e
            print("No gyro on SDA={} SCL={}, trying next pins...".format(sda, scl))
    print_gyro_help(GYRO_SDA_PIN, GYRO_SCL_PIN)
    raise last_err


def run():
    print("Drone starting (ESP32 S3 Mini)")
    print("Motor GPIOs:", MOTOR_PINS)
    print("Throttle (no pot):", THROTTLE_MANUAL)

    try:
        imu, sda, scl = connect_gyro()
        print("Gyro OK on SDA={}, SCL={}".format(sda, scl))
    except OSError:
        print("Waiting — fix gyro wires, then stop (Ctrl+C) and run again.")
        while True:
            time.sleep(1)

    motors = MotorBank()
    motors.off()

    print("Ready. Keep THROTTLE_MANUAL at 0 until bench tests.")

    try:
        while True:
            gx, gy, gz = imu.read_gyro_dps()
            ax, ay, az = imu.read_accel_g()
            throttle = read_throttle()
            fl, fr, rl, rr = mix_motors(throttle, gx, gy, gz)
            motors.set_four(fl, fr, rl, rr)

            print(
                "T={:.2f} M {:.2f},{:.2f},{:.2f},{:.2f} | g {:.1f},{:.1f},{:.1f}".format(
                    throttle, fl, fr, rl, rr, gx, gy, gz
                )
            )
            time.sleep(LOOP_DT)
    except KeyboardInterrupt:
        print("Stop — motors off.")
        motors.off()


if __name__ == "__main__":
    run()