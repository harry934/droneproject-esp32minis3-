# Drone project — simple documentation

For **pin verification, safety, testing stages, and smartphone architecture**, read **[TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md)**.

For **step by step soldering and wire connections**, read **[WIRING_INSTRUCTIONS.md](WIRING_INSTRUCTIONS.md)**.

For **your parts** (2 ESCs, 3 bus bars, LiPo, capacitor, frame, jumpers), read **[HARDWARE_BUILD.md](HARDWARE_BUILD.md)**.

## What this project is

A **4 motor drone controller** on the **Seeed XIAO ESP32 S3**. It reads **MPU6050** and a **throttle potentiometer**, then sets **four motor outputs** (PWM) for ESCs or test LEDs.

## Two Python files (Thonny)

| File | Purpose |
|------|---------|
| **`main.py`** | **All pin numbers** (motors, gyro I2C, throttle). Main loop, PWM, mixing. |
| **`gyroscope.py`** | **MPU6050** driver and calibration. |

Upload **both** files. Change wiring only in the **pin block at the top of `main.py`**.

## How to connect the pins (summary)

**Power:** MPU and pot use **3V3** and **GND** on the XIAO. Motor battery goes to **ESC power only**, not the XIAO.

| XIAO | Wire to |
|------|---------|
| 3V3 | MPU6050 VCC; pot outer leg |
| GND | MPU6050 GND; pot outer leg; ESC signal grounds (common) |
| D4 | MPU6050 SDA |
| D5 | MPU6050 SCL |
| D0 | Pot **center** leg (wiper) |
| D1 | Front left motor ESC signal |
| D2 | Front right motor ESC signal |
| D3 | Rear left motor ESC signal |
| D8 | Rear right motor ESC signal |

Full details, ESC power, LED test wiring, and checklist: **[WIRING_INSTRUCTIONS.md](WIRING_INSTRUCTIONS.md)**.

## Pin table (XIAO labels)

| Job | XIAO pin | GPIO in code |
|-----|----------|----------------|
| Motor front left | D1 | 2 |
| Motor front right | D2 | 3 |
| Motor rear left | D3 | 4 |
| Motor rear right | D8 | 7 |
| Gyro SDA | D4 | 5 |
| Gyro SCL | D5 | 6 |
| Throttle pot | D0 | 1 |

## What the program does each loop (~50 Hz)

1. Read **gyro**.
2. Read **throttle** from the pot.
3. **Mix** throttle and gyro into four motor powers.
4. Output **PWM** on D1, D2, D3, D8.

On startup, gyro **calibration ~2 seconds** — keep the board still.

## How to run in Thonny

1. Install **MicroPython** on the XIAO ESP32 S3.
2. Save `main.py` and `gyroscope.py` to the device.
3. Run `main.py` (F5).

See `THONNY_SETUP.md` for flash and troubleshooting.

## Safety

Learning controller only. **Low throttle**, **props off**, frame secured for motor tests.