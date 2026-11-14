# How to connect the pins (XIAO ESP32 S3)

Step by step wiring for this project. Pin names match **`main.py`** on the **Seeed XIAO ESP32 S3** (standard, not Sense/Plus unless noted).

**Before you start**

1. Power **off** USB and motor battery.
2. Use **3.3 V logic** only on the MPU6050 (never 5 V on VCC).
3. Tie all **GND** together (XIAO, MPU6050, pot, ESC signal grounds).
4. Motor battery powers **ESCs only**, not the XIAO.

---

## Quick map: XIAO pin → wire goes to

| XIAO pin | Connect to |
|----------|------------|
| **3V3** | MPU6050 **VCC**; potentiometer **leg 1** (one outer leg) |
| **GND** | MPU6050 **GND**; pot **leg 3** (other outer leg); each ESC **GND** (signal ground) |
| **D4** | MPU6050 **SDA** |
| **D5** | MPU6050 **SCL** |
| **D0** | Potentiometer **middle leg** (wiper) |
| **D1** | Front left ESC **signal** (or LED anode via resistor) |
| **D2** | Front right ESC **signal** |
| **D3** | Rear left ESC **signal** |
| **D8** | Rear right ESC **signal** |

**Do not use** for this project: D6, D7 (serial/USB), Boot button pad (GPIO0).

---

## 1. MPU6050 gyroscope module

Module labels vary (VCC/VS, GND, SCL, SDA). Match by function.

| From (XIAO) | To (MPU6050) | Notes |
|-------------|--------------|--------|
| **3V3** | **VCC** (or VDD) | Red wire typical |
| **GND** | **GND** | Black wire typical |
| **D4** | **SDA** | I2C data |
| **D5** | **SCL** | I2C clock |

**Optional:** Leave **AD0** unconnected (address `0x68`). If AD0 is wired to **3V3**, address becomes `0x69` and code must change.

**INT, XDA, XCL:** not used in this project.

**After wiring:** Upload code and check serial for `I2C scan: ['0x68']`.

---

## 2. Throttle potentiometer (10 kΩ typical)

A pot has **three legs**. You need one outer leg at 3.3 V, one at GND, middle to D0.

| From (XIAO) | To (pot) |
|-------------|----------|
| **3V3** | **Leg A** (outer) |
| **GND** | **Leg C** (outer) |
| **D0** | **Leg B** (wiper, center) |

If throttle moves backwards in software, swap the two **outer** legs (keep center on D0).

**Never** connect 5 V to the pot on this board; use **3V3** only.

---

## 3. Four motors (ESC signal wires)

View the quad from above, **front** forward (USB end or your chosen front):

```
        FRONT
    FL         FR
         X
    RL         RR
        REAR
```

| Motor position | XIAO pin | ESC channel |
|----------------|----------|-------------|
| Front left (FL) | **D1** | Signal / PWM in |
| Front right (FR) | **D2** | Signal / PWM in |
| Rear left (RL) | **D3** | Signal / PWM in |
| Rear right (RR) | **D8** | Signal / PWM in |

**Per ESC (signal side only for now)**

| From (XIAO) | To (ESC) |
|-------------|----------|
| **D1** (or D2, D3, D8) | **Signal** (sometimes labeled PWM, S, or white/orange wire) |
| **GND** | **GND** on ESC (same ground as XIAO) |

**Power side (separate from XIAO)**

| From (battery PDB) | To (ESC) |
|--------------------|----------|
| Battery **+** (via PDB) | ESC **B+** / red power |
| Battery **−** | ESC **B−** / black power |

ESC **signal ground** must connect to **XIAO GND**. Many builds use a **4 in 1 ESC**: run four signal wires to D1, D2, D3, D8 and one **common GND** to XIAO **GND**.

**3.3 V vs 5 V:** XIAO outputs 3.3 V. Use ESCs that accept 3.3 V logic **or** use a level shifter if the ESC datasheet requires 5 V.

**Test without flying:** Connect a **470 Ω resistor + LED** instead of ESC: GPIO pin → resistor → LED anode → LED cathode → **GND**. Brightness shows motor level in current firmware.

---

## 4. Recommended assembly order

1. **GND bus:** Solder or breadboard a shared ground line from XIAO **GND** to MPU **GND**, pot ground leg, and (later) ESC grounds.
2. **MPU6050:** 3V3, GND, D4, D5 only (four wires).
3. **Pot:** 3V3, GND, D0 (three wires).
4. **USB only:** Flash MicroPython, run I2C scan and pot read tests.
5. **One motor output:** Single LED + resistor on **D1**; verify PWM in loop.
6. **Remaining motors:** D2, D3, D8.
7. **ESC signals last**, still **no props**, battery disconnected or fuse out.
8. **Battery to ESC** only when signal wiring is verified.

---

## 5. Connection checklist (power on)

Check with a multimeter **before** first power on:

| Check | Expected |
|-------|----------|
| 3V3 to GND | **No** short (not 0 Ω) |
| MPU VCC to GND | **No** short |
| D4/D5 to 3V3 | **Not** hard shorted (I2C lines) |
| Pot wiper D0 | Between 0 V and 3.3 V when turned |
| ESC power | **Not** connected to XIAO 3V3 pin |

---

## 6. If your board is XIAO Sense or Plus

| Board | Change |
|-------|--------|
| **Sense** | Avoid **D8** for RR if you use the SD slot; use **D9** (GPIO8) and update `MOTOR_PINS` in `main.py`. |
| **Plus** | Use the Seeed pin map for that board; do not copy D1–D8 blindly. |

---

## 7. Match software to hardware

If you move a wire, change **`main.py`** at the top:

```python
MOTOR_PINS = (2, 3, 4, 7)   # FL, FR, RL, RR → GPIO numbers
GYRO_SDA_PIN = 5            # D4
GYRO_SCL_PIN = 6            # D5
THROTTLE_PIN = 1            # D0
```

GPIO numbers must equal the **D** pins on the XIAO table (D1 = 2, D2 = 3, etc.).