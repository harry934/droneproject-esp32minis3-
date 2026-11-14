# Drone project — simple documentation

## What this project is

A **4-motor drone controller** on the **Seeed XIAO ESP32-S3** (ESP32-S3 Mini). It reads a **gyroscope (MPU6050)** and a **throttle potentiometer**, then sets **four motor outputs** (PWM). In Wokwi, motors are shown as **LEDs**; on a real quad you would connect **ESCs** to the same GPIOs.

---

## Two Python files (Thonny)

| File | Purpose |
|------|---------|
| **`main.py`** | **All pin numbers** (motors, gyro I2C, throttle). Runs the drone loop, PWM, and mixing. |
| **`gyroscope.py`** | **MPU6050 only**: I2C setup, calibration, read gyro (°/s) and accel (g). |

Upload **both** files to the board. `main.py` imports `gyroscope.py`.

To change wiring, edit **only the pin block at the top of `main.py`**.

---

## Pin table (XIAO labels)

| Job | XIAO pin | GPIO in code |
|-----|----------|----------------|
| Motor front-left | D1 | 2 |
| Motor front-right | D2 | 3 |
| Motor rear-left | D3 | 4 |
| Motor rear-right | D8 | 7 |
| Gyro SDA | D4 | 5 |
| Gyro SCL | D5 | 6 |
| Throttle pot | D0 | 1 |

MPU6050: **3V3**, **GND**, **SDA → D4**, **SCL → D5**.

---

## Wokwi (browser simulation)

| File | Purpose |
|------|---------|
| **`diagram.json`** | Circuit: XIAO board, 4 LEDs as motors, MPU6050, pot. |
| **`sketch.ino`** | Same logic in **Arduino C++** (if you simulate in Wokwi instead of Thonny). |

Pins in `sketch.ino` match `main.py`.

---

## What the program does each loop (~50 Hz)

1. Read **gyro** (how fast the board is rotating).
2. Read **throttle** from the pot.
3. **Mix** throttle + small gyro corrections into four motor powers.
4. Output **PWM** to each motor pin.

On startup, the gyro is **calibrated for ~2 seconds** — keep the board still.

---

## How to run in Thonny

1. Install **MicroPython** on the XIAO ESP32-S3.
2. Save `main.py` and `gyroscope.py` to the device.
3. Run `main.py` (F5).

See `THONNY_SETUP.md` for flash and troubleshooting.

---

## Files you can ignore (old split)

These were merged into **`main.py`** + **`gyroscope.py`**:

- `config.py`
- `mpu6050.py`
- `motors.py`

You may delete them from the board if you already uploaded them.

---

## Safety

This is a **learning** controller, not a full flight stack. Use **low throttle**, **props off** for tests, and tie down the frame when testing motors.