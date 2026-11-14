"""
MPU6050 gyroscope + accelerometer (MicroPython).

Pin numbers are not defined here — main.py passes SDA/SCL GPIOs into init_gyro().
"""

from machine import I2C, Pin
import time

MPU6050_ADDR = 0x68

REG_PWR_MGMT_1 = 0x6B
REG_GYRO_CONFIG = 0x1B
REG_ACCEL_CONFIG = 0x1C
REG_ACCEL_XOUT_H = 0x3B
REG_GYRO_XOUT_H = 0x43
REG_WHO_AM_I = 0x75

GYRO_FS_500 = 1
GYRO_SCALE_500 = 65.5


def _read_i16(bus, reg):
    hi, lo = bus.readfrom_mem(MPU6050_ADDR, reg, 2)
    val = (hi << 8) | lo
    if val >= 0x8000:
        val -= 0x10000
    return val


class MPU6050:
    def __init__(self, i2c):
        self.i2c = i2c
        self.gyro_scale = GYRO_SCALE_500

        who = i2c.readfrom_mem(MPU6050_ADDR, REG_WHO_AM_I, 1)[0]
        if who not in (0x68, 0x70, 0x71):
            raise OSError("MPU6050 not found (WHO_AM_I=0x{:02x})".format(who))

        i2c.writeto_mem(MPU6050_ADDR, REG_PWR_MGMT_1, b"\x00")
        time.sleep_ms(100)
        i2c.writeto_mem(MPU6050_ADDR, REG_GYRO_CONFIG, bytes([GYRO_FS_500 << 3]))
        i2c.writeto_mem(MPU6050_ADDR, REG_ACCEL_CONFIG, b"\x00")

        self._gx_off = 0.0
        self._gy_off = 0.0
        self._gz_off = 0.0

    def calibrate_gyro(self, samples=200, delay_ms=5):
        sx = sy = sz = 0.0
        for _ in range(samples):
            gx, gy, gz = self.read_gyro_raw()
            sx += gx
            sy += gy
            sz += gz
            time.sleep_ms(delay_ms)
        n = float(samples)
        self._gx_off = sx / n
        self._gy_off = sy / n
        self._gz_off = sz / n

    def read_gyro_raw(self):
        gx = _read_i16(self.i2c, REG_GYRO_XOUT_H)
        gy = _read_i16(self.i2c, REG_GYRO_XOUT_H + 2)
        gz = _read_i16(self.i2c, REG_GYRO_XOUT_H + 4)
        return gx, gy, gz

    def read_accel_raw(self):
        ax = _read_i16(self.i2c, REG_ACCEL_XOUT_H)
        ay = _read_i16(self.i2c, REG_ACCEL_XOUT_H + 2)
        az = _read_i16(self.i2c, REG_ACCEL_XOUT_H + 4)
        return ax, ay, az

    def read_gyro_dps(self):
        gx, gy, gz = self.read_gyro_raw()
        s = self.gyro_scale
        return (
            (gx - self._gx_off) / s,
            (gy - self._gy_off) / s,
            (gz - self._gz_off) / s,
        )

    def read_accel_g(self):
        ax, ay, az = self.read_accel_raw()
        return ax / 16384.0, ay / 16384.0, az / 16384.0


def init_gyro(sda_pin, scl_pin, i2c_id=0, i2c_freq=400_000, calibrate=True):
    """
    Start I2C, connect MPU6050, optional gyro zero calibration.
    Returns an MPU6050 instance ready for read_gyro_dps() / read_accel_g().
    """
    i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=i2c_freq)
    found = i2c.scan()
    print("I2C scan:", [hex(a) for a in found])

    imu = MPU6050(i2c)
    if calibrate:
        print("Gyro calibration — hold still...")
        imu.calibrate_gyro(samples=200, delay_ms=10)
    return imu