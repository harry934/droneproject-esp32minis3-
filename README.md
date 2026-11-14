# Drone wiring guide for beginners

This project uses an **ESP32 S3 Mini** (small computer board) to read a **gyro sensor** and tell **four motors** how fast to spin. You upload code with **Thonny**.

**Phone control:** `main.py` starts WiFi **MiniDrone** (password `flyhigh123`). On your phone, join that network and open **http://192.168.4.1** for the joystick. Props off until bench tests pass.

**You do not need a potentiometer.**

For a simple USB test without WiFi, run **`main_bench.py`** instead (motors stay at `THROTTLE_MANUAL = 0.0` unless you change it).

---

## Start here: what to do first

Follow these **phases in order**. Do not skip ahead. If a step fails, **stop** and fix it before the next phase.

| Phase | What you do | Battery plugged in? | Where to read |
|-------|-------------|---------------------|---------------|
| **0. Get ready** | Lay out all parts. Props **off**. Battery **unplugged**. Read **Rule number 1** below. | No | This table |
| **1. Program the ESP32** | USB into the ESP32. Install MicroPython in Thonny. Upload **`main.py`**, **`mpu6050.py`**, **`gyroscope.py`**. Run once (errors are OK if gyro not wired yet). | No | [THONNY_SETUP.md](THONNY_SETUP.md) + **Step F** below |
| **2. Wire gyro only** | Connect **only** MPU-6050 to ESP32 (3V3, GND, D4, D5). Run code again; check that the gyro is found (`0x68`). | No | **Step D** below |
| **3. Build frame + motor power** | Mount motors and red driver boards. Wire **bus bars**, **capacitor**, thick wires to both boards. Connect each motor’s **red + blue** wires to **AO/BO** outputs (Step C). | No | **Steps A, B, C** below |
| **4. Signal wires** | Thin jumpers: ESP32 **D1, D2, D3, D8** to each motor **signal** on the controllers. One **GND** wire from ESP32 to **signal GND** on both controllers (same ground as gyro). | No | **Step E** below |
| **5. Bench test** | `THROTTLE_MANUAL = 0.0`. Plug battery **last**. Motors should stay quiet. Then try a tiny value (`0.15`) only with **no props**. | Yes (phase 5 only) | **Step G** below |
| **6. Phone test** | Join WiFi `MiniDrone`, open `http://192.168.4.1`, throttle low, arm only with props off. | Yes (careful) | **Step H** below |

**Your first action today:** do **Phase 0**, then **Phase 1** (USB + Thonny only). Do **not** connect the lithium battery until **Phase 5**.

**Quick path if you only have one hour:** Phase 0 → Phase 1 → Phase 2 (gyro + USB). Save motor wiring for the next session.

---

## Parts you have

1. **ESP32 S3 Mini** … the brain (runs the program)  
2. **MPU-6050** … the gyro (feels tilt and spin)  
3. **4 motors** … spin the propellers  
4. **2 motor controllers** … boards that send power to the motors  
5. **3 bus bars** … each has **3 screws**; we use bar **1 = +**, bar **2 = −**, bar **3 = ground hub** (see Step B)  
6. **Lithium battery** … powers the motors only  
7. **Capacitor** … small part that smooths battery power (goes on + and − near the controllers)  
8. **Frame** … holds everything  
9. **Female to male jumper wires** … plastic wires with different ends  
10. **Female to female jumper wires** … both ends are sockets  

---

## Words that help

| Word | Simple meaning |
|------|----------------|
| **GND** / ground | The **minus** side of power. All black wires meet here. |
| **3V3** | **3.3 volts**. Safe power for the gyro and the small board. **Not** the big battery. |
| **Signal wire** | Thin wire that says “how fast” to spin. **Not** the thick battery wire. |
| **Motor controller** | Box that takes battery power and a signal, then spins a motor. |
| **Bus bar** | Metal strip with **3 screws**; each screw is one **input** you bolt a wire onto. Split battery power without many splices. |

---

## Red motor driver: what the pin names mean

Your **red board** is a **dual motor driver**. It has **two channels** — **A** and **B** — so **one board** can spin **two motors**. Labels on cheap boards differ slightly; this table is what **AO1**, **PWMA**, etc. usually mean.

### Power pins (thick battery wires)

| Name on board | Stands for | Connect to |
|---------------|------------|------------|
| **VM** | **V**oltage **M**otor (motor power in) | Bus bar **+** (battery plus, through thick wire) |
| **GND** | **G**rou**n** **D** (minus / return) | Bus bar **−** (battery minus, thick wire) |
| **VCC** | Logic power for the chip | ESP32 **3V3** (thin wire — **not** the battery) |

Some boards print **+** / **−** next to VM/GND instead of the letters **VM** / **GND**.

| Also seen as | Same as |
|--------------|---------|
| **VIN**, **M+**, **VMS** | Motor power **+** → bar **+** |
| **M−**, **PGND** | Motor power **−** → bar **−** |

### Enable pin (if your board has it)

| Name | Meaning | Connect to |
|------|---------|------------|
| **STBY** | **St**and**by** — chip off until this is high | **3V3** on ESP32 (always “on” while flying) |

If there is **no** STBY pin, ignore this row.

### Motor outputs (your motor’s red + blue wires)

These are the **only** pins that get the motor’s two wires. The driver pushes battery power out here to spin the motor.

| Name | Meaning | What to hook up |
|------|---------|-----------------|
| **AO1** | **A** channel **o**utput terminal **1** | One wire from motor A (red or blue) |
| **AO2** | **A** channel **o**utput terminal **2** | The other wire from motor A |
| **BO1** | **B** channel **o**utput terminal **1** | One wire from motor B |
| **BO2** | **B** channel **o**utput terminal **2** | The other wire from motor B |

| Also seen as | Same as |
|--------------|---------|
| **OUTA1** / **OUTA2** | **AO1** / **AO2** |
| **OUTB1** / **OUTB2** | **BO1** / **BO2** |
| **M1A** / **M1B** | Often motor A’s two outputs |

**AO1 vs AO2:** They are the two motor output screws. In this project: motor **red → AO1**, motor **blue → AO2** (and **red → BO1**, **blue → BO2** on channel B). Swap red ↔ blue on those two screws only if that motor spins backward.

### Speed inputs (from ESP32 — one per motor)

| Name | Meaning | Connect to |
|------|---------|------------|
| **PWMA** | **P**ulse **W**idth **M**odulation, channel **A** (speed command for motor A) | ESP32 **D1** or **D3** (see Step E table) |
| **PWMB** | Speed command for channel **B** | ESP32 **D2** or **D8** |

**PWM** = the ESP32 sends a fast on/off pattern; more “on” time = faster spin. Your code uses pins **D1, D2, D3, D8** for the four motors.

### Direction inputs (set spin direction once with jumpers)

The driver needs to know **which way** current flows through the motor. You wire these **once** to **3V3** and **GND** (not to the ESP32, unless you add fancy code later).

| Name | Meaning | Typical hookup for one fixed direction |
|------|---------|----------------------------------------|
| **AIN1** | **A** channel **in**put **1** (direction bit 1) | **3V3** |
| **AIN2** | **A** channel **in**put **2** (direction bit 2) | **GND** |
| **BIN1** | **B** channel direction bit 1 | **3V3** |
| **BIN2** | **B** channel direction bit 2 | **GND** |

| AIN1 | AIN2 | Motor A tends to… |
|------|------|-------------------|
| 3V3 | GND | Spin one way (pick this first) |
| GND | 3V3 | Spin the opposite way |

Same table applies to **BIN1** / **BIN2** for motor B. If only one motor is backward, swap **AIN1 ↔ AIN2** for that channel, or swap **AO1 ↔ AO2**.

### Gyro (MPU-6050) pin names (for Step D)

| Name | Meaning |
|------|---------|
| **VCC** | Sensor **V**oltage supply → **3V3** |
| **GND** | Ground → **GND** |
| **SDA** | **S**erial **D**ata (I2C) → **D4** |
| **SCL** | **S**erial **C**lock (I2C) → **D5** |

---

## Rule number 1 (read twice)

There are **two separate power systems**:

| What | Powered by |
|------|------------|
| ESP32 board + gyro sensor | **USB cable** into the ESP32 (when learning) |
| Motors | **Lithium battery** only |

**Never** connect the big battery to the ESP32 board.  
**Never** use thin jumper wires for battery power (they will melt).

---

## The ESP32 board: which pins to use

Look at the **side of your ESP32 S3 Mini**. Find these printed names:

| Name on board | Connect to |
|---------------|------------|
| **3V3** | Gyro **VCC** (power for sensor) |
| **GND** | Gyro **GND** + motor controller **signal ground** |
| **D4** | Gyro **SDA** |
| **D5** | Gyro **SCL** |
| **D1** | **Front left** motor **signal** |
| **D2** | **Front right** motor **signal** |
| **D3** | **Rear left** motor **signal** |
| **D8** | **Rear right** motor **signal** |

**Front** = the direction you want the drone to fly forward when you build it.

If your board does not show D1, D2, etc., use the instruction sheet that came in the box.

---

## Build step by step (do in this order)

### Step A: Get the frame ready

1. Screw the **4 motors** onto the arms.  
2. **Do not** put propellers on yet.  
3. Decide which arm is **front left**, **front right**, **rear left**, **rear right**.  
4. Write it on paper. You will need it later.

### Step B: Three bus bars — which screw gets which wire

**Battery unplugged** until this whole step is checked twice.

Each **bus bar** is a metal strip with **3 screws** (3 connection points). Treat them as **screw 1**, **screw 2**, **screw 3** reading left to right when the strip faces you (or use the labels on your kit if it prints **IN / OUT / OUT**).

**Bar roles in this project**

| Bus bar | Rail | Voltage |
|---------|------|---------|
| **Bus bar 1** | **Plus (+)** | Battery positive — **red** wires only (thick) |
| **Bus bar 2** | **Minus (−)** | Battery negative — **black** wires only (thick) |
| **Bus bar 3** | **Common ground hub** | Same as minus, but for **thin** grounds (ESP32, gyro, driver logic GND) |

**You must link bar 2 and bar 3:** Run **one short thick or medium black wire** from **any screw on bar 2** to **screw 1 on bar 3**. That way “ground hub” is really the same as battery minus.

---

#### Bus bar 1 — POSITIVE (+) — 3 screws

| Screw | Connect this wire | Goes to |
|-------|-------------------|---------|
| **1** | **Thick red** from battery **+** (or XT60 main positive) | **Only** the battery feeds here (one wire in) |
| **2** | **Thick red** | Red driver **board 1** → **VM** (motor power +) |
| **3** | **Thick red** | Red driver **board 2** → **VM** (motor power +) |

**Capacitor + leg:** Connect to **screw 2 or 3** on bar 1 (same metal strip as VM). Long leg or side marked **+**.

Do **not** put ESP32, gyro, or motor red/blue wires on bar 1.

---

#### Bus bar 2 — NEGATIVE (−) — 3 screws

| Screw | Connect this wire | Goes to |
|-------|-------------------|---------|
| **1** | **Thick black** from battery **−** (main ground) | Battery return (one wire in) |
| **2** | **Thick black** | Red driver **board 1** → **GND** (motor power minus, big pin) |
| **3** | **Thick black** | Red driver **board 2** → **GND** (motor power minus, big pin) |

**Capacitor − leg:** Connect to **screw 2 or 3** on bar 2 (striped / short leg to **−** only).

---

#### Bus bar 3 — GROUND HUB (thin wires OK) — 3 screws

After **bar 2 screw 1** (or any bar 2 screw) is tied to **bar 3 screw 1** with a **black** wire:

| Screw | Connect this wire | Goes to |
|-------|-------------------|---------|
| **1** | **Black** (medium or thick) | **From bus bar 2** (same minus as battery) — see above |
| **2** | **Thin black** jumper | ESP32 **GND** |
| **3** | **Thin black** jumper | Red driver **board 1 GND** (logic) **and** daisy-chain to **board 2 GND** if you only have one screw free |

**MPU-6050 GND:** Do **not** need its own bar screw. Wire **MPU GND → ESP32 GND** (one wire between boards), then ESP32 **GND** → bar 3 screw 2.

If you run out of screw 3 space: tie both drivers’ **GND** pins together with one thin black wire, then **one** wire from that junction to bar 3.

**Never** put battery **+** on bar 2 or bar 3. **Never** put motor red/blue wires on any bus bar.

---

#### Order to tighten (helps avoid mistakes)

1. Mount all **three bars** on the frame (insulated from metal if the frame is conductive).  
2. Wire **bar 1** screws 1→2→3 (battery +, VM, VM).  
3. Wire **bar 2** screws 1→2→3 (battery −, GND, GND).  
4. Install **capacitor** between bar 1 and bar 2.  
5. Wire **bar 3** (bar 2 → bar 3, then ESP32 GND, then driver grounds).  
6. **Check** with a multimeter if you have one: bar 1 vs bar 2 = battery voltage; bar 3 vs bar 2 = **0 Ω** (same ground).  
7. Plug battery **last**, only when Steps C and E are done and props are off.

```
  BATTERY (+) -----> [Bar1 screw1] [Bar1 screw2]--VM  board1
                                    [Bar1 screw3]--VM  board2
                           cap (+) --^

  BATTERY (-) -----> [Bar2 screw1] [Bar2 screw2]--GND board1
                                    [Bar2 screw3]--GND board2
                           cap (-) --^
                                    |
                    black link      |
                           [Bar3 screw1] [Bar3 screw2]-- ESP32 GND
                                         [Bar3 screw3]-- driver GND(s)
                                         MPU GND -----> ESP32 GND
```

### Step C: Motors to the red driver boards (blue + red wire motors)

*(Pin names **AO1**, **BO2**, **VM**, etc. are explained in the section **Red motor driver: what the pin names mean** above.)*

Your motors are **small brushed DC motors**: only **two thin wires** (often **red** and **blue**). That matches the **red dual motor driver** boards (H-bridge), **not** a 3-wire brushless ESC.

**Each red board runs 2 motors.** You have **2 boards** → **4 motors** total.

On the red board, motor wires screw or solder into **two outputs per channel** (motor **out**puts, not power from the battery):

| Motor channel | Motor wires go here | Plain English |
|---------------|---------------------|---------------|
| Motor A | **AO1** and **AO2** | **A** motor, **out**put screw 1 and 2 |
| Motor B | **BO1** and **BO2** | **B** motor, **out**put screw 1 and 2 |

#### Same color rule on every motor (use this project-wide)

We use **one rule for all four motors** so you do not have to guess:

| Motor wire color | Screw on red driver | Same as |
|------------------|---------------------|---------|
| **RED** | **1** on that channel → **AO1** (motor A) or **BO1** (motor B) | “Output 1” |
| **BLUE** | **2** on that channel → **AO2** (motor A) or **BO2** (motor B) | “Output 2” |

Short memory trick: **R**ed → screw **1** (**AO1** / **BO1**). **Blue → 2** (**AO2** / **BO2**).

If **one** motor spins the wrong way when you test (prop would blow air the wrong way), fix **only that motor**: swap **red and blue** on **AO1 ↔ AO2** (or **BO1 ↔ BO2**). Do not change the other three motors unless they are wrong too.

#### Exact connections (copy this to paper)

| Corner | Board | Channel | **RED wire →** | **BLUE wire →** |
|--------|-------|---------|----------------|-----------------|
| **Front left (FL)** | 1 | A | **AO1** | **AO2** |
| **Front right (FR)** | 1 | B | **BO1** | **BO2** |
| **Rear left (RL)** | 2 | A | **AO1** | **AO2** |
| **Rear right (RR)** | 2 | B | **BO1** | **BO2** |

**How to wire each motor (repeat four times):**

1. Find the arm labeled **FL**, **FR**, **RL**, or **RR** on your frame.  
2. Hold the motor so you can see the **red** and **blue** cable coming out of it.  
3. Screw or clamp **red** into **output 1** (**AO1** or **BO1** from the table).  
4. Screw or clamp **blue** into **output 2** (**AO2** or **BO2**).  
5. Tug gently — screws must bite the metal, not squash through insulation only.

If your motor only has **black + red** (no blue), treat **black like blue**: **red → AO1/BO1**, **black → AO2/BO2**.

**Do not** plug motor red/blue wires into the **battery bus bars**. Motor power comes **through the red board** only: battery → **VM** (+) and **GND** (−) on the board → then out to the motor via **AO1/AO2** or **BO1/BO2**.

**Still no battery** until Step B power and Step E signals are done.

### Step D: Gyro to ESP32 (thin jumpers)

The gyro is a small board with 4 pins: **VCC, GND, SDA, SCL**.

| ESP32 pin | Gyro pin |
|-----------|----------|
| **3V3** | **VCC** |
| **GND** | **GND** |
| **D4** | **SDA** |
| **D5** | **SCL** |

**Which jumper?**

- Gyro has **metal pins sticking up** → use **female to female** on those pins.  
- ESP32 holes may need **female to male** (pin into the board, socket on the wire).

Tape the gyro flat in the **middle of the frame** so it moves with the drone.

### Step E: ESP32 to the red driver boards (speed + direction)

*(See **Red motor driver: what the pin names mean** for **PWMA**, **AIN1**, **STBY**, etc.)*

These are **thin jumper wires**. They tell **how fast** to spin; they do **not** power the motors.

**On each red board you need:**

1. **VCC** — chip logic power → ESP32 **3V3** (small power for the driver IC).  
2. **STBY** (if present) — **standby** enable → **3V3** so the driver is not asleep.  
3. **GND** — logic ground → ESP32 **GND** (must match gyro GND and motor **GND** on the same board).  
4. **Speed pins** — **PWMA** / **PWMB** (**P**ulse **W**idth **M**odulation = speed knob from code):

| Motor | ESP32 | Red board pin | Meaning |
|-------|-------|---------------|---------|
| Front left | **D1** | **PWMA** on board 1 | Speed for channel **A**, motor FL |
| Front right | **D2** | **PWMB** on board 1 | Speed for channel **B**, motor FR |
| Rear left | **D3** | **PWMA** on board 2 | Speed for channel **A**, motor RL |
| Rear right | **D8** | **PWMB** on board 2 | Speed for channel **B**, motor RR |

5. **Direction pins** — **AIN1/AIN2** (channel A) and **BIN1/BIN2** (channel B): digital **in**puts that pick spin direction:

| Pins | Hook to | Meaning |
|------|---------|---------|
| **AIN1** | **3V3** | Direction input 1 for motor A |
| **AIN2** | **GND** | Direction input 2 for motor A |
| **BIN1** | **3V3** | Direction input 1 for motor B |
| **BIN2** | **GND** | Direction input 2 for motor B |

If a motor spins backward, swap **AIN1 ↔ AIN2** for that channel only, or swap **AO1 ↔ AO2** on the motor wires.

**Ground recap:** Motor **GND** (thick) → **bar 2**. ESP32 + gyro + driver logic **GND** (thin) → **bar 3**, with **bar 3 linked to bar 2** (Step B table).

All grounds must meet: battery minus, bar 2, bar 3, driver power GND, driver logic GND, ESP32 GND, gyro GND.

```
        BIG BATTERY (motors only)
              |
         bus bars + cap
              |
    motor controller 1 ---- motor controller 2
         |    |                  |    |
       4 motors on the frame

    SMALL WIRES (brain talks to controllers)
    ESP32 D1 D2 D3 D8  --->  signal pins
    ESP32 GND         --->  signal GND on both controllers

    SMALL WIRES (brain reads gyro)
    ESP32 3V3 GND D4 D5  --->  MPU-6050
```

### Step F: Put code on the ESP32 (before battery test)

1. Install **MicroPython** and **Thonny** (see `THONNY_SETUP.md`).  
2. Copy these files to the board: **`main.py`**, **`mpu6050.py`**, **`gyroscope.py`**.  
3. Run `main.py`.  
4. In the Shell you should see **I2C scan** with **`0x68`**, then WiFi **MiniDrone** and an IP like **192.168.4.1**.  
5. If scan is **`[]`**, fix **Step D** wiring before arming anything.

Optional: upload **`main_bench.py`** for a no-WiFi gyro + motor printout test.

### Step G: First battery test (careful)

1. Propellers **still off**.  
2. `THROTTLE_MANUAL` is **0.0**.  
3. Plug the battery in.  
4. Motors should **not** spin hard.  
5. If something smells hot or buzzes wrong, **unplug the battery right away**.

To try a **very small** spin later (still no props): use **`main_bench.py`** with `THROTTLE_MANUAL = 0.15`, then set back to `0.0`.

### Step H: Control from your phone

1. Props **off**. Battery only when you are ready for a bench test.  
2. Reset or run `main.py` on the ESP32. Wait for **Join WiFi 'MiniDrone'** in the Shell.  
3. On the phone: **Settings → Wi‑Fi → MiniDrone**, password **`flyhigh123`**.  
4. Open a browser: **http://192.168.4.1**  
5. Leave throttle **down**. Tap **Arm** only when the drone is still and gyro calibration finished.  
6. Raise throttle slowly. If the phone loses WiFi for more than ~0.5 s, motors **cut** (failsafe).

---

## Mistakes beginners often make

| Do not do this | Why |
|----------------|-----|
| Battery + to ESP32 3V3 | Breaks the board |
| Battery through jumper wires | Fire risk |
| Gyro VCC to battery or 5 V | Breaks the sensor |
| Thick motor power wire to D1, D2, D3, D8 | Those pins are **signals only** |

---

## Before you fly (later)

This firmware includes **phone control**, **arming**, and **failsafe**, but it is still **learning** code. Props stay off until:

1. I2C scan shows **0x68** every boot.  
2. Your **red dual motor boards** are wired (PWM to D1–D3, D8; direction pins set; battery on VM only).  
3. Bench tests with low throttle show sane motor direction.

More detail: [TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md).

---

## Files in this folder

| File | What it is |
|------|------------|
| `main.py` | Phone WiFi + flight control |
| `mpu6050.py` | Thin API for `main.py` (`read()`, `calibrate_gyro()`) |
| `gyroscope.py` | Low-level MPU-6050 driver |
| `main_bench.py` | Optional simple test without WiFi |
| `THONNY_SETUP.md` | How to install MicroPython |
| `COMPONENTS_WIRING_GUIDE.md` | Same wiring ideas as this README |

---

## If you get stuck

Send photos of:

1. Both motor controllers (so we can read the labels).  
2. Your battery label.  
3. One motor (show if it has 2 or 3 wires).  

We can then tell you **exactly** which screw or pin is which.