# Drone project for ESP32 S3 Mini (XIAO)

Four motor learning controller on the **Seeed XIAO ESP32 S3**. **MicroPython** in Thonny: `main.py` + `gyroscope.py`. Reads **MPU6050** over I2C and a **throttle pot**, then drives four **PWM** motor outputs.

**Confirm before wiring:** Board model (XIAO ESP32 S3, **Sense**, or **Plus**), ESC type, battery, and whether you use a separate flight controller. Pin tables below assume the **standard XIAO ESP32 S3**.

## Executive summary

| Area | Status |
|------|--------|
| Pin map vs XIAO silkscreen | Matches Seeed map for standard XIAO ESP32 S3 |
| MPU6050 I2C | Implemented, address `0x68`, 400 kHz |
| Motor outputs | 1 kHz `duty_u16` PWM, **not** standard 50 Hz ESC pulses |
| Arming, disarm, failsafe | **Not implemented** |
| Smartphone control | **Not implemented** (planned architecture below) |
| Safe for props on | **No**. Educational mixer, ~50 Hz loop, no attitude PID |

Static Python check only (`py_compile`). **You must run hardware tests** on your board.

## Project files

| File | Purpose |
|------|---------|
| `main.py` | All pin numbers, motors, mixer, main loop |
| `gyroscope.py` | MPU6050 driver and calibration |
| `DOCUMENTATION.md` | Short how to run guide |
| `WIRING_INSTRUCTIONS.md` | Step by step pin and wire connections |
| `HARDWARE_BUILD.md` | Your BOM: bus bars, 2 ESCs, battery, capacitor, frame |
| `TECHNICAL_REVIEW.md` | Same specification as this README (standalone copy) |
| `THONNY_SETUP.md` | Flash MicroPython in Thonny |

Upload `main.py` and `gyroscope.py` to the device. Change wiring only in the **pin block at the top of `main.py`**.

## Pin table (XIAO silkscreen)

| Job | XIAO pin | GPIO | Signal | Voltage |
|-----|----------|------|--------|---------|
| Motor front left | D1 | 2 | PWM out | 3.3 V logic |
| Motor front right | D2 | 3 | PWM out | 3.3 V logic |
| Motor rear left | D3 | 4 | PWM out | 3.3 V logic |
| Motor rear right | D8 | 7 | PWM out | 3.3 V logic |
| Gyro SDA | D4 | 5 | I2C | 3.3 V |
| Gyro SCL | D5 | 6 | I2C | 3.3 V |
| Throttle pot wiper | D0 | 1 | ADC in | 0 to 3.3 V |
| MPU6050 power | 3V3 | | Supply | 3.3 V |
| Common ground | GND | | Ground | 0 V |

**Unused on purpose:** D6, D7 (UART/USB), Boot (GPIO0), user LED (GPIO21).

## How to connect the pins

Power **off** USB and battery before wiring. All **GND** wires must meet at the XIAO **GND**. Use **3V3** only for the MPU6050 (never 5 V on the sensor).

### MPU6050

| XIAO | MPU6050 pin |
|------|-------------|
| 3V3 | VCC |
| GND | GND |
| D4 | SDA |
| D5 | SCL |

### Throttle potentiometer (3 legs)

| XIAO | Pot leg |
|------|---------|
| 3V3 | One outer leg |
| GND | Other outer leg |
| D0 | Center leg (wiper) |

If throttle is reversed, swap the two outer legs only.

### Four motors (ESC signal)

Quad viewed from above, front forward:

| Position | XIAO signal pin |
|----------|-----------------|
| Front left | D1 |
| Front right | D2 |
| Rear left | D3 |
| Rear right | D8 |

For **each** ESC: **signal** wire to the matching D pin; **ESC GND** to **XIAO GND**. Battery **+** and **−** go to the ESC power inputs only, not to the XIAO.

**Bench test:** Pin → **470 Ω resistor** → LED anode → LED cathode → **GND** (same D pins as above).

**Full checklist, assembly order, and Sense/Plus notes:** [WIRING_INSTRUCTIONS.md](WIRING_INSTRUCTIONS.md).

**Restrictions**

1. **GPIO3 on D2 (motor FR):** ESP32 S3 strapping at reset. If boot fails, move FR to **D9** (GPIO8).
2. **XIAO Sense:** D8 may conflict with on board SD clock. Remap rear right motor off D8.
3. **XIAO Plus:** Different pinout. Reverify against [Seeed wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/).
4. **ESC signals:** Many ESCs want **50 Hz, 1000 to 2000 µs** and sometimes **5 V** tolerant inputs. XIAO GPIO is **3.3 V**. Check your ESC datasheet.
5. **Motor power:** Battery and PDB only. **Never** power motors from the XIAO 3.3 V pin.

## Wiring (logical)

```
              MPU6050
    3V3 ---- VCC
    GND ---- GND
    D4  ---- SDA
    D5  ---- SCL

              XIAO ESP32 S3
    3V3 ---- pot top
    D0  ---- pot wiper
    GND ---- pot bottom
    D1  ---- ESC or LED front left signal
    D2  ---- ESC or LED front right signal
    D3  ---- ESC or LED rear left signal
    D8  ---- ESC or LED rear right signal
    GND ---- ESC signal ground (common with XIAO)

    Motor battery ---- ESC power only (not XIAO)
```

## How components talk to the ESP32

### MPU6050

| Item | Detail |
|------|--------|
| Protocol | I2C, 400 kHz, `I2C(0)` |
| Pins | SDA GPIO5 (D4), SCL GPIO6 (D5) |
| Address | `0x68` (AD0 low) |
| Library | `gyroscope.py` only (no pip packages) |
| Update rate | ~50 Hz in main loop |
| Failure today | Caught at init (WHO_AM_I). No runtime watchdog |

### Throttle potentiometer

| Item | Detail |
|------|--------|
| Protocol | ADC on GPIO1 (D0) |
| Update rate | ~50 Hz |

### Motors (four outputs)

| Item | Detail |
|------|--------|
| Protocol today | `machine.PWM` at 1000 Hz, duty 0 to 65535 |
| Typical ESC need | 50 Hz servo PWM; **code change required** for real ESCs |
| Mixer layout | Quad X: FL, FR, RL, RR |

## What the code does now

1. Calibrate gyro ~2 s (**hold still**).
2. Each loop (~50 Hz): read gyro, read pot, mix, set four PWM outputs.
3. Stop in Thonny with keyboard interrupt turns motors off.

**Gaps:** No arming switch, no phone link, no disconnect failsafe, no PID stabilization.

## Code reliability notes

| Part | Risk |
|------|------|
| `mix_motors()` | Gyro feedforward only; not a flight grade PID |
| Pot | No smoothing; noisy pot jitters motors |
| After calibration | Motors can spin if pot is above deadband |
| ESC waveform | Wrong shape for most brushless ESCs until updated |

**Hardware tests still required:** MicroPython on your chip, I2C scan `0x68`, PWM on each pin, full bench run 5+ minutes.

## Smartphone control (planned, not coded)

**Recommended first version**

| Item | Choice |
|------|--------|
| Radio | WiFi 2.4 GHz on ESP32 S3 |
| Phone UI | Web page in browser (Android or iOS) |
| Network | SoftAP (phone joins drone) or home WiFi |
| Commands | WebSocket or HTTP JSON, 20 to 50 Hz |
| Telemetry | Gyro, armed flag, RSSI, battery when wired |

**Command flow (target)**

1. Phone sends throttle, roll, pitch, yaw, arm flag.
2. ESP32 validates ranges and arm rules (gyro OK, throttle low).
3. Mixer drives four motors.
4. If no valid packet for **200 ms**, **disarm** and idle motors.

**On disconnect or bad data:** disarm within 200 ms.

**ESP32 vs flight controller:** This repo runs one loop on the ESP32 (OK for bench). For props on flight, add full PID plus arming plus failsafe on ESP32, **or** send RC to a commercial flight controller.

## Safety checklist

| Hazard | Current | Should add |
|--------|---------|------------|
| Wrong wiring | Pin table in `main.py` | Verify before solder |
| MPU on 5 V | | Use 3.3 V only |
| I2C fault | Stop at init | Disarm and no spin at runtime |
| Surprise motor start | Deadband only | Arm command, motors off at boot |
| Phone lost | N/A | Timeout disarm |
| Software hang | None | Watchdog |
| Props on too early | | Follow test stages below |

**Proposed arming:** Power on motors off → gyro cal → throttle zero → explicit arm → disarm on fault, timeout, or user command.

## Staged testing

| Stage | What to do | Pass | Stop if |
|-------|------------|------|---------|
| 0 | Confirm board model | Matches this table | Wrong pins |
| 1 | Flash MicroPython, REPL | `import machine` works | Cannot flash |
| 2 | I2C scan | `0x68` seen | No MPU |
| 3 | Gyro only | ~0 °/s still, ~1 g on Z | Bad WHO_AM_I |
| 4 | Pot ADC | Smooth 0 to 100% | Floating pin |
| 5 | One motor pin + LED | PWM changes output | Wrong GPIO |
| 6 | Four outputs, **no props**, no ESC battery | All independent | Overheat |
| 7 | Full `main.py` 5 min bench | Stable serial | Reset or heat |
| 8 | WiFi phone (when built) | Timeout disarm works | Motors spin on loss |
| 9 | ESC 50 Hz code (when built) | Throttle follows | Wrong pulse |
| 10 | Props on, tethered only | Controlled hover | Oscillation or link loss |

## Run in Thonny

1. Install **MicroPython** for ESP32 S3 on the XIAO.
2. Save `main.py` and `gyroscope.py` to the board.
3. Run `main.py` (F5). Keep the board still during gyro calibration.

Details: `THONNY_SETUP.md`.

## Known limitations

1. Not flight certified.
2. ESC timing mismatch until servo style PWM is added.
3. GPIO3 strapping on D2 motor FR.
4. Sense board SD conflict on D8 possible.
5. No battery ADC, baro, or magnetometer.
6. Smartphone control not in firmware yet.

## Information we still need from you

1. Exact board photo or product link.
2. ESC model and required signal (PWM µs, DSHOT, etc.).
3. Battery voltage and connector.
4. Phone control: WiFi web, BLE, or RC transmitter.
5. Separate flight controller yes or no.

## References

[Seeed XIAO ESP32 S3 pin map](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)

[ESP32 S3 boot and strapping](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html)

[MPU6050](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/)