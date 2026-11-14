/*
 * Quad drone firmware — Seeed XIAO ESP32-S3 (ESP32-S3 Mini)
 *
 * Motors (PWM / LED): D1,D2,D3,D8  → GPIO 2,3,4,7
 * MPU6050 I2C:        D4,D5         → GPIO 5 (SDA), 6 (SCL)
 * Throttle pot:       D0            → GPIO 1
 */

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

const int SDA_PIN = 5;
const int SCL_PIN = 6;

const int THROTTLE_POT_PIN = 1;

// FL, FR, RL, RR
const int MOTOR_PINS[4] = {2, 3, 4, 7};

const float YAW_K = 0.8f;
const float ROLL_K = 0.6f;
const float PITCH_K = 0.6f;
const int MOTOR_MIN = 0;
const int MOTOR_MAX = 255;

Adafruit_MPU6050 mpu;

static float gyroToDegPerSec(float radPerSec) {
  return radPerSec * 180.0f / PI;
}

static int throttleFromPot() {
  int raw = analogRead(THROTTLE_POT_PIN);
  return map(raw, 0, 4095, MOTOR_MIN, MOTOR_MAX);
}

static void setMotors(int fl, int fr, int rl, int rr) {
  int speeds[4] = {fl, fr, rl, rr};
  for (int i = 0; i < 4; i++) {
    speeds[i] = constrain(speeds[i], MOTOR_MIN, MOTOR_MAX);
    analogWrite(MOTOR_PINS[i], speeds[i]);
  }
}

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(MOTOR_PINS[i], OUTPUT);
    analogWrite(MOTOR_PINS[i], 0);
  }

  Serial.begin(115200);
  delay(100);

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found — wire SDA to D4, SCL to D5, 3V3, GND.");
    while (true) {
      delay(1000);
    }
  }

  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("XIAO ESP32-S3 quad");
  Serial.println("Motors: D1,D2,D3,D8 | I2C: D4,D5 | Pot: D0");
}

void loop() {
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  float gx = gyroToDegPerSec(gyro.gyro.x);
  float gy = gyroToDegPerSec(gyro.gyro.y);
  float gz = gyroToDegPerSec(gyro.gyro.z);

  int base = throttleFromPot();

  int roll = (int)(gx * ROLL_K);
  int pitch = (int)(gy * PITCH_K);
  int yaw = (int)(gz * YAW_K);

  int fl = base + pitch + roll - yaw;
  int fr = base + pitch - roll + yaw;
  int rl = base - pitch + roll + yaw;
  int rr = base - pitch - roll - yaw;
  setMotors(fl, fr, rl, rr);

  Serial.print("Throttle=");
  Serial.print(base);
  Serial.print("  M ");
  Serial.print(fl);
  Serial.print(",");
  Serial.print(fr);
  Serial.print(",");
  Serial.print(rl);
  Serial.print(",");
  Serial.print(rr);
  Serial.print("  gyro ");
  Serial.print(gx, 1);
  Serial.print(",");
  Serial.print(gy, 1);
  Serial.print(",");
  Serial.println(gz, 1);

  delay(20);
}