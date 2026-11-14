"""
Drone main program — Seeed XIAO ESP32-S3 (Thonny / MicroPython).

All GPIO assignments live in this file (motors + gyro I2C + throttle).
Gyro sensor logic is in gyroscope.py.
"""

import time
from machine import Pin, ADC, PWM

from gyroscope import init_gyro

# =============================================================================
# PIN ALLOCATION (change only here)
# Board silkscreen → GPIO
# =============================================================================

# Motors FL, FR, RL, RR  —  D1, D2, D3, D8
MOTOR_PINS = (2, 3, 4, 7)

# MPU6050 I2C  —  D4 = SDA, D5 = SCL
GYRO_I2C_ID = 0
GYRO_SDA_PIN = 5
GYRO_SCL_PIN = 6
GYRO_I2C_FREQ = 400_000

# Throttle potentiometer  —  D0
THROTTLE_PIN = 1

# =============================================================================
# TUNING
# =============================================================================

MOTOR_PWM_HZ = 1000
PWM_MAX = 65535

ROLL_GAIN = 0.6
PITCH_GAIN = 0.6
YAW_GAIN = 0.8

THROTTLE_DEADBAND = 0.05
LOOP_DT = 0.02

# =============================================================================
# MOTORS
# =============================================================================

class MotorBank:
    def __init__(self, pins=MOTOR_PINS):
        self._pwms = []
        for p in pins:
            self._pwms.append(PWM(Pin(p), freq=MOTOR_PWM_HZ, duty_u16=0))

    def off(self):
        self.set_four(0, 0, 0, 0)

    def set_four(self, fl, fr, rl, rr):
        for i, level in enumerate((fl, fr, rl, rr)):
            level = max(0.0, min(1.0, level))
            duty = 0 if level <= 0 else int(level * PWM_MAX)
            self._pwms[i].duty_u16(duty)


# =============================================================================
# THROTTLE & MIXER
# =============================================================================

_throttle_adc = ADC(Pin(THROTTLE_PIN))
_throttle_adc.atten(ADC.ATTN_11DB)


def read_throttle():
    raw = _throttle_adc.read()
    t = raw / 4095.0
    if t < THROTTLE_DEADBAND:
        return 0.0
    return t


def mix_motors(base, gx, gy, gz):
    roll = gx * ROLL_GAIN / 100.0
    pitch = gy * PITCH_GAIN / 100.0
    yaw = gz * YAW_GAIN / 100.0

    fl = base + pitch + roll - yaw
    fr = base + pitch - roll + yaw
    rl = base - pitch + roll + yaw
    rr = base - pitch - roll - yaw

    def clamp(v):
        return max(0.0, min(1.0, v))

    return clamp(fl), clamp(fr), clamp(rl), clamp(rr)


# =============================================================================
# RUN
# =============================================================================


def run():
    print("Drone starting (XIAO ESP32-S3)")
    print("Motor GPIOs:", MOTOR_PINS)
    print("Gyro I2C SDA={}, SCL={}".format(GYRO_SDA_PIN, GYRO_SCL_PIN))

    imu = init_gyro(GYRO_SDA_PIN, GYRO_SCL_PIN, GYRO_I2C_ID, GYRO_I2C_FREQ)
    motors = MotorBank()
    motors.off()

    print("Ready — pot on D0 (GPIO {})".format(THROTTLE_PIN))

    try:
        while True:
            gx, gy, gz = imu.read_gyro_dps()
            ax, ay, az = imu.read_accel_g()
            throttle = read_throttle()
            fl, fr, rl, rr = mix_motors(throttle, gx, gy, gz)
            motors.set_four(fl, fr, rl, rr)

            print(
                "T={:.2f} M {:.2f},{:.2f},{:.2f},{:.2f} | g {:.1f},{:.1f},{:.1f}".format(
                    throttle, fl, fr, rl, rr, gx, gy, gz
                )
            )
            time.sleep(LOOP_DT)
    except KeyboardInterrupt:
        print("Stop — motors off.")
        motors.off()


if __name__ == "__main__":
    run()