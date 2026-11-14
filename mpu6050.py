"""
MPU6050 driver API used by main.py (phone / WebSocket flight code).
Same chip as gyroscope.py; this module matches imu.read() expectations.
"""

from gyroscope import MPU6050 as _Driver


class MPU6050:
    def __init__(self, i2c):
        self._imu = _Driver(i2c)

    def calibrate_gyro(self, samples=200, delay_ms=10):
        print("Calibrating gyro — keep the drone still...")
        self._imu.calibrate_gyro(samples=samples, delay_ms=delay_ms)

    def read(self):
        """ax, ay, az in g. gx, gy, gz in degrees per second."""
        ax, ay, az = self._imu.read_accel_g()
        gx, gy, gz = self._imu.read_gyro_dps()
        return ax, ay, az, gx, gy, gz