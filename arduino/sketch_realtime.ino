#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const int FLEX_PINS[5] = {36, 34, 35, 32, 33};
const int NUM_FLEX = 5;
const unsigned long SAMPLE_INTERVAL = 100; // ms
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(230400); // higher baud rate for faster transmission
  Wire.begin();

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed");
    while (1);
  }
  Serial.println("flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ,timestamp_us");
}

void loop() {
  unsigned long now = millis();
  if (now - lastSampleTime < SAMPLE_INTERVAL) return;
  lastSampleTime = now;

  int flex[NUM_FLEX];
  for (int i = 0; i < NUM_FLEX; i++) {
    flex[i] = analogRead(FLEX_PINS[i]);
  }

  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Build CSV line in a single string
  String line = "";
  for (int i = 0; i < NUM_FLEX; i++) {
    line += String(flex[i]) + ",";
  }
  line += String(ax) + "," + String(ay) + "," + String(az) + ",";
  line += String(gx) + "," + String(gy) + "," + String(gz) + ",";
  line += String(micros()); // high-precision timestamp
  Serial.println(line);
}
