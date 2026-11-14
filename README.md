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
| **3. Build frame + motor power** | Mount motors and controllers on the frame. Wire **bus bars**, **capacitor**, thick wires from bars to **both** controllers. Connect **3 motor wires** from each motor to a controller. | No | **Steps A, B, C** below |
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

### Step C: Motors to controllers (thick motor wires)

Each motor usually has **3 thick colored wires**. Plug them into **one motor output** on a controller (labels like M1, M2, or A B C).

1. Connect **front left** motor to a free channel. Write down: “FL = controller __ channel __”.  
2. Do the same for **FR**, **RL**, **RR**.

**Still no battery plugged in** if you are not sure the wires are correct.

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

### Step E: ESP32 to motor controllers (thin signal wires)

These wires only **tell** the speed. They do **not** carry motor battery power.

For **each** motor, find the small **signal** pin on the controller (may say **S**, **PWM**, or **SIG**):

| Motor corner | ESP32 pin | Goes to |
|--------------|-----------|---------|
| Front left | **D1** | That motor’s **signal** pin |
| Front right | **D2** | Signal |
| Rear left | **D3** | Signal |
| Rear right | **D8** | Signal |

**One black wire:** ESP32 **GND** → **signal GND** on **both** motor controllers (and it should already meet gyro **GND**).

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