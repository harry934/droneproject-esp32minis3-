"""
MPU6050 gyroscope + accelerometer (MicroPython).

Used by mpu6050.py (phone flight main.py) and main_bench.py (simple test loop).
"""

from machine import I2C, Pin
import time

MPU6050_ADDR = 0x68
MPU6050_ADDR_ALT = 0x69


def _pick_addr(found):
    if MPU6050_ADDR in found:
        return MPU6050_ADDR
    if MPU6050_ADDR_ALT in found:
        return MPU6050_ADDR_ALT
    return None

REG_PWR_MGMT_1 = 0x6B
REG_GYRO_CONFIG = 0x1B
REG_ACCEL_CONFIG = 0x1C
REG_ACCEL_XOUT_H = 0x3B
REG_GYRO_XOUT_H = 0x43
REG_WHO_AM_I = 0x75

GYRO_FS_500 = 1
GYRO_SCALE_500 = 65.5


def _read_i16(bus, addr, reg):
    hi, lo = bus.readfrom_mem(addr, reg, 2)
    val = (hi << 8) | lo
    if val >= 0x8000:
        val -= 0x10000
    return val


class MPU6050:
    def __init__(self, i2c, addr=None):
        self.i2c = i2c
        self.gyro_scale = GYRO_SCALE_500
        if addr is None:
            found = i2c.scan()
            addr = _pick_addr(found)
            if addr is None:
                raise OSError("ENODEV: MPU6050 not on bus (scan={})".format(
                    [hex(a) for a in found]
                ))
        self.addr = addr

        who = i2c.readfrom_mem(self.addr, REG_WHO_AM_I, 1)[0]
        if who not in (0x68, 0x70, 0x71):
            raise OSError("MPU6050 bad WHO_AM_I=0x{:02x}".format(who))

        i2c.writeto_mem(self.addr, REG_PWR_MGMT_1, b"\x00")
        time.sleep_ms(100)
        i2c.writeto_mem(self.addr, REG_GYRO_CONFIG, bytes([GYRO_FS_500 << 3]))
        i2c.writeto_mem(self.addr, REG_ACCEL_CONFIG, b"\x00")

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
        a = self.addr
        gx = _read_i16(self.i2c, a, REG_GYRO_XOUT_H)
        gy = _read_i16(self.i2c, a, REG_GYRO_XOUT_H + 2)
        gz = _read_i16(self.i2c, a, REG_GYRO_XOUT_H + 4)
        return gx, gy, gz

    def read_accel_raw(self):
        a = self.addr
        ax = _read_i16(self.i2c, a, REG_ACCEL_XOUT_H)
        ay = _read_i16(self.i2c, a, REG_ACCEL_XOUT_H + 2)
        az = _read_i16(self.i2c, a, REG_ACCEL_XOUT_H + 4)
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


def _scan_bus(i2c_id, sda_pin, scl_pin, freq):
    i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
    return i2c, i2c.scan()


def print_gyro_help(sda_pin, scl_pin):
    print("")
    print("*** MPU6050 NOT FOUND (I2C scan was empty) ***")
    print("")
    print("The ESP32 cannot see the gyro. Fix wiring (README Phase 2):")
    print("  ESP32 3V3  -> MPU VCC")
    print("  ESP32 GND  -> MPU GND")
    print("  ESP32 D4   -> MPU SDA   (GPIO {}, now SDA={})".format(5, sda_pin))
    print("  ESP32 D5   -> MPU SCL   (GPIO {}, now SCL={})".format(6, scl_pin))
    print("")
    print("Also check:")
    print("  - Wires fully pushed into the sockets")
    print("  - Swap SDA and SCL if still empty")
    print("  - MPU powered from 3V3, NOT battery")
    print("  - If D4/D5 fail, try SDA=GPIO 8, SCL=GPIO 9 in main.py")
    print("")
    print("Re-run after fixing wires. Stop with Ctrl+C in Thonny.")
    print("")


def init_gyro(sda_pin, scl_pin, i2c_id=0, i2c_freq=400_000, calibrate=True):
    """Start I2C, find MPU6050 at 0x68, calibrate if asked."""
    freq_try = (i2c_freq, 100_000)
    found_any = []

    for freq in freq_try:
        i2c, found = _scan_bus(i2c_id, sda_pin, scl_pin, freq)
        found_any = found
        print("I2C scan SDA={} SCL={} @{}Hz:".format(sda_pin, scl_pin, freq), [hex(a) for a in found])
        addr = _pick_addr(found)
        if addr is not None:
            imu = MPU6050(i2c, addr=addr)
            if calibrate:
                print("Gyro calibration — hold still...")
                imu.calibrate_gyro(samples=200, delay_ms=10)
            return imu

    print_gyro_help(sda_pin, scl_pin)
    raise OSError("ENODEV: no MPU6050 on I2C (scan={})".format([hex(a) for a in found_any]))