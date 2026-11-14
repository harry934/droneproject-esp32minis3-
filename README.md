# Drone project for ESP32 S3 Mini (XIAO)

This is a **four motor** drone controller for the **Seeed XIAO ESP32 S3**. It reads an **MPU6050** gyroscope and a **throttle potentiometer**, then drives **four PWM motor outputs** for ESCs or test LEDs.

## Project files

| File | Purpose |
|------|---------|
| `main.py` | Pin numbers for motors, gyro I2C, and throttle. Main loop, PWM, and motor mixing. |
| `gyroscope.py` | MPU6050 setup, calibration, gyro in degrees per second, accel in g. |
| `DOCUMENTATION.md` | Extended notes and wiring reference. |
| `THONNY_SETUP.md` | How to flash MicroPython and upload code in Thonny. |

Upload **`main.py`** and **`gyroscope.py`** to the board. Change wiring only in the **pin block at the top of `main.py`**.

## Pin table (XIAO silkscreen)

| Job | XIAO pin | GPIO |
|-----|----------|------|
| Motor front left | D1 | 2 |
| Motor front right | D2 | 3 |
| Motor rear left | D3 | 4 |
| Motor rear right | D8 | 7 |
| Gyro SDA | D4 | 5 |
| Gyro SCL | D5 | 6 |
| Throttle pot | D0 | 1 |

Connect the MPU6050 to **3V3**, **GND**, **SDA on D4**, and **SCL on D5**.

## What the code does

On startup the gyro is calibrated for about two seconds. **Keep the board still** during that time.

Each loop (about 50 times per second):

1. Read rotation rate from the gyro.
2. Read throttle from the potentiometer.
3. Mix throttle with small roll, pitch, and yaw corrections.
4. Send PWM to all four motor pins.

## Run in Thonny

1. Install **MicroPython** on the XIAO ESP32 S3.
2. Save `main.py` and `gyroscope.py` to the MicroPython device.
3. Open `main.py` and press **F5** to run.

More steps are in `THONNY_SETUP.md`.

## Safety

This is a **learning** controller, not a full flight computer. Test with **low throttle**, **props removed**, and the frame secured when spinning motors.