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
5. **3 bus bars** … metal strips that split battery power to both controllers  
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
| **Bus bar** | Thick metal rail so one battery wire can feed many places. |

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

**AO1 vs AO2:** Neither is “plus” or “minus” by itself. They are the two ends of the motor. Swap AO1 ↔ AO2 if the prop spins the wrong way.

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

### Step B: Battery power (thick wires only)

**Battery unplugged the whole time while you wire this part.**

1. Connect battery **minus (−)** to **bus bar 2** (negative bar).  
2. Connect battery **plus (+)** to **bus bar 1** (positive bar).  
3. From bar **+**, run thick wire to **power +** on **motor controller 1** and **motor controller 2**.  
4. From bar **−**, run thick wire to **power −** on **both** controllers.  
5. Put the **capacitor** across bar **+** and bar **−** close to the controllers.  
   - Long leg or **+** marked side → positive bar.  
   - Striped or short leg → negative bar.  
6. Use **bus bar 3** the way your kit says, or connect extra **ground** wires there so everything shares the same minus.

### Step C: Motors to the red driver boards (blue + red wire motors)

*(Pin names **AO1**, **BO2**, **VM**, etc. are explained in the section **Red motor driver: what the pin names mean** above.)*

Your motors are **small brushed DC motors**: only **two thin wires** (often **red** and **blue**). That matches the **red dual motor driver** boards (H-bridge), **not** a 3-wire brushless ESC.

**Each red board runs 2 motors.** You have **2 boards** → **4 motors** total.

On the red board, motor wires screw or solder into **two outputs per channel** (motor **out**puts, not power from the battery):

| Motor channel | Motor wires go here | Plain English |
|---------------|---------------------|---------------|
| Motor A | **AO1** and **AO2** | **A** motor, **out**put screw 1 and 2 |
| Motor B | **BO1** and **BO2** | **B** motor, **out**put screw 1 and 2 |

**Red vs blue:** On cheap motors the colors are not always “plus and minus.” Pick one wire to **AO1** and one to **AO2**. If the motor spins **backward** later, **swap** the two motor wires on that output only.

**Suggested layout (write this on paper):**

| Corner | Red board | Channel | Motor wires |
|--------|-----------|---------|-------------|
| Front left (FL) | Board 1 | A (AO1/AO2) | red + blue |
| Front right (FR) | Board 1 | B (BO1/BO2) | red + blue |
| Rear left (RL) | Board 2 | A | red + blue |
| Rear right (RR) | Board 2 | B | red + blue |

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

**Bus bar 3:** Use it as an extra **ground** rail if helpful — tie **battery −**, both board **GND** pins, and ESP32 **GND** to the same minus so everything shares one ground.

All grounds must meet: battery minus, controller power minus, controller signal minus, ESP32 GND, gyro GND.

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