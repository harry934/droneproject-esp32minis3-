# Technical review and system specification

**Status date:** 2026-03-14  
**Target board (assumed):** [Seeed Studio XIAO ESP32 S3](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) (ESP32 S3 Mini class board, **not** DevKitC).  
**Firmware in repo:** MicroPython (`main.py`, `gyroscope.py`) for Thonny.

> **Confirm before wiring:** Exact board SKU (XIAO ESP32 S3, **Sense**, or **Plus**), motor type (ESC + brushless vs brushed), battery (voltage, capacity), and whether a separate flight controller board exists. This document flags **Sense/Plus** conflicts where they differ.

---

## Executive summary

| Area | Status |
|------|--------|
| Pin map vs XIAO silkscreen | **Consistent** with Seeed pin map for standard XIAO ESP32 S3 |
| I2C gyro (MPU6050) | **Implemented**; address `0x68`; 400 kHz; no runtime re-check after init |
| Motor outputs | **Implemented** as 1 kHz `duty_u16` PWM — **not** standard ESC servo pulses |
| Arming / disarm / failsafe | **Not implemented** |
| Smartphone control | **Not implemented** (architecture below) |
| Flight ready for props on | **No** — educational mixer only, ~50 Hz loop, no PID attitude control |

**Python syntax:** `main.py` and `gyroscope.py` compile with `py_compile` (static check only; **not** flashed-hardware tested from this environment).

---

## 1. Code verification and reliability

### 1.1 Stack

| Layer | Item | Notes |
|-------|------|--------|
| Hardware | XIAO ESP32 S3 | 3.3 V logic; 5 V on `5V` pin is **USB input**, not for direct MPU power |
| Runtime | MicroPython for ESP32 S3 | Must match your chip (USB, PSRAM variant). Install via Thonny |
| Dependencies | **None** (stdlib only: `machine`, `time`) | No `upip` packages required for current code |
| Modules | `main.py` → imports `gyroscope.py` | Both must be on the device filesystem |

### 1.2 Logic review

| Function | Behaviour | Risk |
|----------|-----------|------|
| `init_gyro()` | I2C scan, WHO_AM_I check, wake, ±500 °/s gyro, 2 s calibration | **Abort** with `OSError` if MPU missing; `main.run()` does not catch → **hard stop** (motors never start — acceptable) |
| `read_throttle()` | ADC 12-bit, deadband 5% | No smoothing; noisy pot may jitter motors |
| `mix_motors()` | Open-loop throttle + gyro feedforward | **Not** a stabilising PID; can **amplify** oscillations if gains too high |
| `MotorBank.set_four()` | Clamps 0…1, PWM duty | Motors can spin **immediately** after calibration if pot > deadband — **no arm switch** |
| Main loop | 50 Hz (`LOOP_DT = 0.02`) | Too slow for aggressive attitude control; OK for bench LED tests |
| `KeyboardInterrupt` | Calls `motors.off()` | **No** watchdog, **no** disconnect failsafe |

### 1.3 What was **not** tested (must be done on your hardware)

1. MicroPython build runs on **your** XIAO revision.  
2. PWM on GPIO 2, 3, 4, 7 drives **your** ESCs or LEDs correctly.  
3. I2C at 400 kHz is stable with **your** wire length and pull-ups (module usually has pull-ups).  
4. Loop timing under WiFi (when added) does not starve the control loop.  
5. Combined behaviour: pot + gyro + four outputs for 10+ minutes without reset.

### 1.4 Validation process (recommended order)

See [Section 6](#6-testing-and-validation).

---

## 2. GPIO and hardware pin verification

### 2.1 Official XIAO ESP32 S3 map (Seeed wiki)

| XIAO | GPIO | Used in project | Function on chip |
|------|------|-----------------|------------------|
| D0 | 1 | Throttle ADC | ADC1_CH0, touch |
| D1 | 2 | Motor FL | PWM capable |
| D2 | 3 | Motor FR | PWM; **strapping** (JTAG source at reset) — see §2.3 |
| D3 | 4 | Motor RL | PWM capable |
| D4 | 5 | I2C SDA | I2C + ADC |
| D5 | 6 | I2C SCL | I2C + ADC |
| D8 | 7 | Motor RR | PWM; SPI SCK alias |
| D6 | 43 | **Unused** | USB/UART TX — keep free for serial |
| D7 | 44 | **Unused** | USB/UART RX |
| Boot | 0 | **Unused** | Strapping — do not tie heavy loads |
| User LED | 21 | **Unused** | On-board indicator |

### 2.2 Complete pin assignment table (project)

| Component | XIAO pin | GPIO | Signal | Voltage | Direction | Purpose |
|-----------|----------|------|--------|---------|-----------|---------|
| MPU6050 VCC | 3V3 | — | Power | 3.3 V | In | Sensor supply |
| MPU6050 GND | GND | — | Ground | 0 V | — | Common ground |
| MPU6050 SDA | D4 | 5 | I2C SDA | 3.3 V | Bidir | IMU data |
| MPU6050 SCL | D5 | 6 | I2C SCL | 3.3 V | Out (host) | IMU clock |
| Pot leg 1 | 3V3 | — | Power | 3.3 V | — | Pot top |
| Pot leg 2 | D0 | 1 | Analog | 0–3.3 V | In | Throttle wiper |
| Pot leg 3 | GND | — | Ground | 0 V | — | Pot bottom |
| Motor FL signal | D1 | 2 | PWM | 3.3 V* | Out | ESC signal or LED anode (via R) |
| Motor FR signal | D2 | 3 | PWM | 3.3 V* | Out | ESC signal or LED |
| Motor RL signal | D3 | 4 | PWM | 3.3 V* | Out | ESC signal or LED |
| Motor RR signal | D8 | 7 | PWM | 3.3 V* | Out | ESC signal or LED |
| ESC / motor GND | GND | — | Ground | 0 V | — | Common with MCU (ESC logic ground) |

\*Many ESCs expect 5 V tolerant **servo PWM** (50 Hz, 1000–2000 µs). XIAO GPIO is **3.3 V**. Use ESCs rated for 3.3 V logic or a level shifter / 5 V BEC on signal if the ESC datasheet requires 5 V.

### 2.3 Restrictions and conflicts

| Topic | Assessment |
|-------|------------|
| **GPIO3 (D2, motor FR)** | ESP32 S3 strapping: JTAG signal source at reset. Avoid strong external pull that fights default at **power-on**. Prefer **D9** for FR if you see boot failures or JTAG oddities. |
| **GPIO2, 4, 7** | No strapping conflict for normal SPI boot. |
| **D4 + D5** | Dedicated I2C on silkscreen; **do not** also use for motors. |
| **D6/D7** | Reserved for UART/USB serial on many setups; **not** assigned in code. |
| **XIAO ESP32 S3 Sense** | D8/D9/D10 share SPI/SD pins on Sense; SD on GPIO7 may conflict if SD card used. **D8 for motor RR** conflicts with on-board SD SCK on Sense — **remap RR** to D9/D10 if you have Sense. |
| **XIAO ESP32 S3 Plus** | Different pinout and B2B connector; **re-verify entire table** against [Plus wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/). |
| **Current per GPIO** | Espressif: ~40 mA per pin max (aggregate limits apply). **ESC signals** are low current; **do not** drive motors directly from GPIO. |

### 2.4 Power

| Rail | Source | Loads |
|------|--------|-------|
| 3.3 V (XIAO) | On-board regulator | ESP32, MPU6050, pot (low current) |
| 5 V (`5V` pin) | USB / VBUS | **Not** for MPU; for peripherals only if spec allows |
| Motor / ESC power | **Separate battery pack** (e.g. 2S–4S LiPo via PDB) | ESCs + motors — **never** from XIAO 3.3 V |

---

## 3. Component communication and integration

### 3.1 MPU6050 (gyro + accelerometer)

| Item | Detail |
|------|--------|
| Purpose | Attitude rate (gyro) and gravity vector (accel) for mixing |
| Protocol | **I2C** (not SPI) |
| Host | ESP32 S3, `I2C(0)`, SDA=GPIO5, SCL=GPIO6 |
| Device address | `0x68` (AD0 low); `0x69` if AD0 → 3.3 V |
| Speed | 400 kHz (`GYRO_I2C_FREQ`) |
| Data format | 16-bit registers; gyro scaled to °/s in software |
| Rate | Read each control loop (~50 Hz) — **below** IMU internal rate |
| Library | Custom `gyroscope.py` (register level), no Adafruit |
| Failure detection | Init: WHO_AM_I + `i2c.scan()`. Runtime: **none** (no stale data check, no timeout) |

**Recommended addition:** If `0x68` not in scan, refuse to arm motors; periodic read retry counter; optional MPU `INT` pin (not wired today).

### 3.2 Throttle potentiometer

| Item | Detail |
|------|--------|
| Purpose | Manual throttle setpoint 0–100% |
| Protocol | **Analog** (ADC) |
| Pin | GPIO1 (D0), `ADC.ATTN_11DB` |
| Rate | Every loop (~50 Hz) |
| Failure | Stuck wiper → fixed throttle; floating pin → erratic ADC — **use 3.3 V/GND wired pot** |

### 3.3 Motor outputs (ESC or test LED)

| Item | Detail |
|------|--------|
| Purpose | Four independent thrust commands (quad X layout) |
| Protocol (today) | **PWM** `machine.PWM`, **1000 Hz**, `duty_u16` 0–65535 |
| Protocol (typical ESC) | **50 Hz**, pulse width **1000–2000 µs** (some 490 Hz DSHOT on dedicated FC) |
| **Gap** | **Code must change** for real ESCs (`esp32.RMT` or servo timing), not only duty cycle |

### 3.4 Wiring diagram (logical)

```
                    ┌─────────────────────────────┐
         3V3 ───────┤ VCC                         │
         GND ───────┤ GND                         │
    D4 (SDA) ───────┤ SDA      MPU6050             │
    D5 (SCL) ───────┤ SCL                         │
                    └─────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   XIAO ESP32 S3    │
    3V3 ────┬───────┤ 3V3                │
    GND ────┼───────┤ GND                │
    D0 ─────┼─ wiper┤ D0    Potentiometer │
            │  GND──┴── GND              │
    D1 ─────────────┤ PWM ──► ESC FL (signal)
    D2 ─────────────┤ PWM ──► ESC FR
    D3 ─────────────┤ PWM ──► ESC RL
    D8 ─────────────┤ PWM ──► ESC RR
                    └───────────────────┘

    ESC power: battery + PDB (NOT from XIAO 3V3)
    ESC GND ↔ XIAO GND (common reference)
```

---

## 4. Smartphone control architecture (design — **not in repo**)

### 4.1 Role split (recommended)

| Responsibility | ESP32 S3 (this project) | Dedicated flight controller (optional) |
|----------------|-------------------------|----------------------------------------|
| WiFi / BLE link to phone | **Yes** | Usually no |
| Command decode, timeouts, arming | **Yes** | Betaflight/iNav: RC layer |
| High-rate gyro PID (200–1000 Hz) | **Weak on current code** | **FC strength** |
| Motor PWM / DSHOT to ESCs | **Yes** (after ESC-safe driver) | **FC** in most builds |
| Blackbox / GPS / advanced nav | Optional on ESP32 | FC or companion |

**Current repo:** ESP32 runs **everything** in one loop — acceptable for **bench / learning** only. For props-on flight, either (a) add full PID + arming + failsafe on ESP32, or (b) use phone → ESP32 → **PPM/SBUS/CRSF to a commercial FC**.

### 4.2 Recommended link: WiFi + web UI (first milestone)

| Item | Choice | Rationale |
|------|--------|-----------|
| Physical | **WiFi** 2.4 GHz | ESP32 S3 has WiFi; no extra radio |
| Phone UI | **Web app** (HTML/JS in browser) | No Play Store build; works Android/iOS |
| Topology | SoftAP `DRONE-AP` **or** join home router STA | SoftAP: phone joins drone network; STA: drone on LAN |
| Transport | **HTTP REST** for telemetry + **WebSocket** for sticks | Low rate commands 20–50 Hz |
| Security | WPA2 on AP; token in header for POST | Minimum for class project; not military grade |

**Command flow:**

1. Phone sends `{"throttle":0.0,"roll":0,"pitch":0,"yaw":0,"arm":false}` at 20–50 Hz.  
2. ESP32 validates: range checks, rate limits, **arm only if gyro OK + throttle low**.  
3. Mixer converts to four motor setpoints (same as today + RC overrides).  
4. **Timeout:** if no packet for **>200 ms**, force **disarm** and minimum throttle.

**Telemetry back (1–5 Hz):**

- Gyro (°/s), accel (g), loop time, armed flag, I2C OK, optional battery ADC, WiFi RSSI (`wlan.status()`).

**BLE alternative:** Lower latency, shorter range, more mobile dev work (nRF Connect / custom app). Use if WiFi coexistence with control loop is problematic.

### 4.3 Disconnect behaviour (required spec)

| Event | Required motor behaviour |
|-------|--------------------------|
| Phone disconnect / WiFi loss | Disarm within **200 ms**, motors idle |
| Invalid JSON / out-of-range | Ignore packet; if repeated, disarm |
| MPU6050 read fail | Disarm immediately |
| Low battery (when wired) | Disarm + alert on phone |

**None of this is coded yet.**

---

## 5. Safety and failure prevention

### 5.1 Checklist

| Hazard | Mitigation (current) | Mitigation (required) |
|--------|----------------------|------------------------|
| Reversed MPU power | — | 3.3 V only; verify before power-on |
| Short on motor battery | — | Fuse; power on with props off |
| Wrong GPIO | Pin table in `main.py` | Re-verify against this doc before solder |
| I2C failure | Crash at init | Disarm; no spin; LED error pattern |
| Gyro drift / vibration | 2 s cal only | Accel gyro fusion; notch filters |
| Unexpected motor spin | Deadband only | **Arm switch**; `motors.off()` at boot |
| USB connected + ESC powered | — | **Remove props**; disconnect USB BEC conflicts |
| Software hang | None | **Watchdog** timer; ESCs stop on signal loss if configured |
| Phone link lost | N/A | Command timeout disarm |
| GPIO3 boot strap (D2) | — | Test boot; consider moving FR off D2 |

### 5.2 Arming procedure (proposed — implement in `main.py`)

1. Power on; motors **off**.  
2. Gyro cal; pot at **zero**; phone shows **DISARMED**.  
3. User arms only via explicit command + throttle low.  
4. Disarm: command, timeout, or sensor fault → immediate `motors.off()`.

---

## 6. Testing and validation

| Stage | Action | Pass criteria | **Stop if** |
|-------|--------|---------------|-------------|
| 0 | Confirm board model (S3 / Sense / Plus) | Matches this document variant | Wrong pin table |
| 1 | USB only, flash MicroPython, REPL | `import machine` works | Cannot flash |
| 2 | I2C scan sketch | `0x68` in scan | No device / wrong wiring |
| 3 | Gyro only (`init_gyro` in REPL) | Stable ~0 °/s still; ~1 g on Z | Wrong WHO_AM_I |
| 4 | Pot ADC | 0–100% monotonic as knob turns | Floating or inverted |
| 5 | One motor pin (LED + resistor) | PWM changes brightness | No output / wrong pin |
| 6 | All four PWM, **no props**, no battery on ESC | Independent control | Overheating ESC |
| 7 | Integrated loop on bench | Serial stable; no resets 5 min | Wobble, reset, heat |
| 8 | WiFi + phone (after implemented) | Commands + timeout disarm | Motors spin on disconnect |
| 9 | ESC 50 Hz firmware (after implemented) | Throttle responds on tach/LED | Wrong pulse width |
| 10 | Props on, tethered / light line | Controlled hover | Any oscillation or loss of link |

---

## 7. Project structure and limitations

### 7.1 Repository layout

```
main.py           # Pins, motors, mixer, main loop
gyroscope.py      # MPU6050 driver
README.md         # Overview
DOCUMENTATION.md  # Short user guide
THONNY_SETUP.md   # Flash MicroPython
TECHNICAL_REVIEW.md  # This file
```

### 7.2 Known limitations

1. **Not flight certified** — no PID, no arming, no failsafe.  
2. **ESC timing wrong** for most brushless ESCs until rewritten.  
3. **GPIO3 (D2)** strapping risk for motor FR.  
4. **Sense** board may conflict on D8 with SD.  
5. **Smartphone control** not implemented.  
6. **No** battery voltage, **no** baro altitude, **no** magnetometer.  
7. Static `py_compile` only — **you** must run hardware tests.

### 7.3 Information still required from you

Reply with:

1. Exact board name (photo or product link).  
2. ESC model and required signal (PWM µs, DSHOT, etc.).  
3. Battery voltage and connector type.  
4. Phone control preference (WiFi web vs BLE vs existing RC transmitter).  
5. Whether a separate flight controller will be used.

---

## References

- [Seeed XIAO ESP32 S3 getting started / pin map](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)  
- [ESP32 S3 strapping pins (Espressif TRM)](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html)  
- [MPU6050 product page / I2C address 0x68](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/)