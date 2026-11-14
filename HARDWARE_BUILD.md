# Wiring your actual parts list

This guide matches **your** hardware:

| Part | Role |
|------|------|
| ESP32 S3 Mini (XIAO) | Brain: reads gyro, sends motor commands |
| MPU-6050 module | Gyro + accelerometer (I2C) |
| 4 motors | Brushless (3 wires each) **or** brushed (2 wires)** — see below |
| 2 motor controllers | Usually **2 ESC boards** (each runs 2 motors) or 2 halves of the quad power train |
| 3 bus bars | Split battery **+** and **−** to both controllers (and optional third bar for extra taps) |
| Lithium battery | Powers **motor controllers only** (not the ESP32 logic directly) |
| Capacitor | Across battery **+** and **−** at the controllers (spike filtering) |
| Female ↔ male jumper wires | ESP32 ↔ MPU6050, ESP32 ↔ ESC **signal** |
| Female ↔ female jumper wires | Extensions; MPU module often has **male** pins → use **F–F** from ESP32 header to MPU pins |
| Frame | Mechanical mount for motors, controllers, battery, flight electronics |

**Not in your list but used in current code:** throttle **potentiometer** on **D0**. Add one for bench tests, or we change code to fixed throttle / phone control later.

**We still need from you:** Photo or model name of the **2 motor controllers** (ESC part number), battery **voltage** (2S / 3S / 4S), and whether motors are **brushless (3 wires)** or **brushed (2 wires)**.

---

## Big picture (two power domains)

```
DOMAIN A — Logic (low power, 3.3 V)
  USB or 3V3 regulator on XIAO
       → ESP32 S3 Mini
       → MPU-6050 (VCC, GND, SDA, SCL)
       → (optional pot on D0)
       → 4× thin signal wires to motor controllers

DOMAIN B — Power (battery, high current)
  LiPo (+) ──► bus bar (+) ──► motor controller 1 B+
           └──► motor controller 2 B+
           ╎
  Capacitor (+) to (−) right here at the controllers

  LiPo (−) ──► bus bar (−) ──► motor controller 1 B−
           └──► motor controller 2 B−
           └──► MUST also tie to ESC/signal GND and ESP32 GND (one common reference)
```

**Never** connect LiPo **+** to the XIAO **3V3** pin. **Never** power motors from the ESP32.

---

## 1. Three bus bars (battery distribution)

Typical use with **two** motor controllers:

| Bus bar | Connect |
|---------|---------|
| **Bar 1 (main +)** | Battery **red / positive** → both controllers’ **battery +** (or B+, VIN+, DC+) |
| **Bar 2 (main −)** | Battery **black / negative** → both controllers’ **battery −** (B−, GND power) |
| **Bar 3** | **Option A:** Second **+** tap (balance leads, fuse, or spare). **Option B:** Dedicated **signal ground** bus feeding all ESC signal grounds and ESP32 **GND**. **Option C:** Frame / arm bonding (check your kit instructions). |

Use the **main fuse** or XT60 from the battery **first**, then short thick wires to the bars. Torque screws so contact is firm (loose bars heat up).

### Capacitor

Solder or bolt the capacitor **across bar 1 (+) and bar 2 (−)** as close as possible to the motor controllers:

| Check | Detail |
|-------|--------|
| **+** leg | Main positive bus |
| **−** leg | Main negative bus |
| Rating | Voltage **above** fully charged LiPo (e.g. **50 V** cap for 3S; **63 V+** for 4S). Typical values **470 µF to 1000 µF** low ESR (ESC kits often ship one). |
| Polarity | Electrolytic caps: **striped / −** side to **negative** only. Wrong polarity can explode. |

---

## 2. Two motor controllers + four motors

Labels differ by brand. Match by **function**, not color alone.

### If brushless (drone style, 3 wires per motor)

Each motor has **three** thick phase wires (A/B/C or U/V/W) to **one** channel on a controller. **Do not** connect battery power to motor wires.

| From | To |
|------|-----|
| Bus bar **+** | Controller 1 power **+**, Controller 2 power **+** |
| Bus bar **−** | Controller 1 power **−**, Controller 2 power **−** |
| Motor 1 (3 wires) | **One** output set on controller 1 (channel M1) |
| Motor 2 (3 wires) | Another channel on controller 1 (M2) |
| Motor 3 (3 wires) | Controller 2 (M1) |
| Motor 4 (3 wires) | Controller 2 (M2) |

**On the frame**, assign corners **FL, FR, RL, RR** and write them down. When you connect **signal** wires from the ESP32, use the table in section 4.

### If brushed DC (2 wires per motor, H-bridge boards)

Unusual on a flying quad but possible on kits. Then each controller has **two** motor outputs (+/− or OUT1/OUT2). Power and ground still go from bus bars to the controller **power** terminals. **Signal** wiring may differ from this repo (we assume **PWM speed control**, not IN1/IN2 direction pins). **Stop** and confirm controller model before applying LiPo.

---

## 3. MPU-6050 ↔ ESP32 S3 Mini (jumpers)

Power the MPU from **3V3**, **not** from the battery bus.

| ESP32 (XIAO) | MPU-6050 | Jumper tip |
|--------------|----------|------------|
| **3V3** | **VCC** | F–M or F–F depending on headers |
| **GND** | **GND** | Black |
| **D4** | **SDA** | I2C |
| **D5** | **SCL** | I2C |

**Jumper ends:**

| Wire type | Use when |
|-----------|----------|
| **Female → male** | XIAO **socket** (needs **male** pin into board) → breadboard or screw terminal |
| **Female → female** | XIAO socket ↔ **male pins** on MPU breakout (both ends socket onto pins) |

Keep I2C wires **short** (under ~15 cm if possible). Share **GND** with the ESC signal ground later.

Mount the MPU **firmly on the frame** near the center (it must feel the airframe tilt/spin, not just vibrate loose).

---

## 4. ESP32 signal wires → both motor controllers

Four **separate** thin wires: one **PWM / signal** per motor. **Plus one logic ground** from ESP32 **GND** to **signal GND** on **each** controller (or one common signal ground that both ESCs share).

Quad viewed from above (**front** = where you want to fly forward):

| Corner | ESP32 pin | Plug to |
|--------|-----------|---------|
| Front left | **D1** | Controller channel **FL** signal |
| Front right | **D2** | Controller channel **FR** signal |
| Rear left | **D3** | Controller channel **RL** signal |
| Rear right | **D8** | Controller channel **RR** signal |
| (all ESC logic) | **GND** | ESP32 **GND** |

**Which controller is FL/FR vs RL/RR** depends how you wired motors in section 2. Keep a **paper diagram** so D1–D8 match the real corner.

Signal names on ESCs: **Signal**, **S**, **PWM**, **white**, **orange** (not the thick red/black power).

---

## 5. Frame assembly order (recommended)

1. Mount **4 motors** on arms (props **off**).
2. Mount **2 motor controllers** with airflow; route **thick** battery wires to **bus bars**.
3. Install **capacitor** on the bars at the controllers.
4. Connect **motor phase wires** to correct controller outputs (no battery yet).
5. Mount **ESP32** and **MPU6050** on the stack/center; soft mount the MPU if you have foam.
6. **Signal** jumpers: D1–D8 and **GND** to both controllers.
7. **Logic ground tie:** ESC signal **GND** ↔ XIAO **GND** (essential).
8. **Battery:** connect to bus bars **last**, with a power switch or removable XT60 if possible.
9. **USB** to XIAO for code and serial **without** props for first tests.

---

## 6. Jumper wire cheat sheet

| Connection | Suggested wire |
|------------|----------------|
| XIAO D4/D5/D1/D2/D3/D8 ↔ ESC signal pins | F–F or F–M, **one conductor per signal** |
| XIAO 3V3/GND ↔ MPU | Short F–F |
| XIAO GND ↔ ESC signal ground | **One solid black** (can use bus bar 3 as ground star) |
| Battery ↔ bus bars | **Not** jumper wire — use silicone/flexible **high current** wire |

Do **not** carry motor battery current through breadboard jumpers.

---

## 7. Power up sequence (safe)

| Step | Action |
|------|--------|
| 1 | Props **removed**, battery **disconnected** |
| 2 | Plug USB → flash/run `main.py` + `gyroscope.py` |
| 3 | Verify **I2C scan** shows `0x68` |
| 4 | Connect **only** ESC signal + GND (no battery) → motor outputs should be idle at boot |
| 5 | Connect battery → **no throttle** / pot at zero → listen for ESC beeps, motors must **not** spin wildly |
| 6 | Low throttle test **per corner** before props |

---

## 8. Match software (`main.py`)

```python
MOTOR_PINS = (2, 3, 4, 7)   # D1, D2, D3, D8
GYRO_SDA_PIN = 5            # D4
GYRO_SCL_PIN = 6            # D5
THROTTLE_PIN = 1            # D0 if you add a pot
```

**Important:** Present firmware uses **1 kHz PWM duty**, not every ESC’s **50 Hz 1000–2000 µs** standard. Confirm with your ESC manual; code may need an update before flight.

---

## 9. What to send us next (so we don’t guess)

1. **Motor controller** model or a clear photo of labels.
2. **Battery:** cell count and connector (e.g. 3S 11.1 V, XT60).
3. **Capacitor** value printed on the can (e.g. 1000 µF 25 V).
4. **Motors:** 3 wires each (brushless) or 2 wires (brushed)?
5. **Bus bar** photo (how your kit expects bar 3 to be used).

Then we can mark **exact** terminals on **your** ESCs and adjust code if signal pins differ.