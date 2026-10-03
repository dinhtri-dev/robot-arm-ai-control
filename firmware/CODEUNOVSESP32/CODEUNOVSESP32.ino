#include <Arduino.h>
#include <SoftwareSerial.h>

/* ================= NHAN LENH TU ESP32-C3 ================= */
// Uno D10 = RX, nhận tín hiệu từ ESP32-C3 GPIO4
// Uno D11 = TX, không dùng nhưng SoftwareSerial cần khai báo
SoftwareSerial espSerial(10, 11);

/* ================= CNC SHIELD V3 PIN ================= */
#define X_STEP 2
#define Y_STEP 3
#define Z_STEP 4

#define X_DIR 5
#define Y_DIR 6
#define Z_DIR 7

#define ENABLE_PIN 8   // LOW = bật driver

/* ================= TOC DO ================= */
// Số càng nhỏ motor càng nhanh
#define STEP_INTERVAL_US 2500
#define STEP_PULSE_US 5

/* ================= CHIEU QUAY ================= */
// Nếu chiều bị ngược thì đổi HIGH thành LOW hoặc ngược lại
#define X_PLUS_DIR HIGH
#define X_MINUS_DIR LOW

#define Y_PLUS_DIR HIGH
#define Y_MINUS_DIR LOW

#define Z_PLUS_DIR HIGH
#define Z_MINUS_DIR LOW

/* ================= TRANG THAI MOTOR ================= */
bool xRun = false;
bool yRun = false;
bool zRun = false;

unsigned long lastXStep = 0;
unsigned long lastYStep = 0;
unsigned long lastZStep = 0;

/* ================= TAO 1 XUNG STEP ================= */
void stepMotor(uint8_t stepPin) {
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(STEP_PULSE_US);
  digitalWrite(stepPin, LOW);
}

/* ================= DUNG TAT CA ================= */
void stopAll() {
  xRun = false;
  yRun = false;
  zRun = false;

  Serial.println("STOP ALL");
}

/* ================= CHAY TUNG TRUC ================= */
void runX(bool dir) {
  xRun = true;
  yRun = false;
  zRun = false;

  digitalWrite(X_DIR, dir);
  Serial.println(dir == X_PLUS_DIR ? "X+" : "X-");
}

void runY(bool dir) {
  xRun = false;
  yRun = true;
  zRun = false;

  digitalWrite(Y_DIR, dir);
  Serial.println(dir == Y_PLUS_DIR ? "Y+" : "Y-");
}

void runZ(bool dir) {
  xRun = false;
  yRun = false;
  zRun = true;

  digitalWrite(Z_DIR, dir);
  Serial.println(dir == Z_PLUS_DIR ? "Z+" : "Z-");
}

/* ================= XU LY LENH ================= */
void handleCommand(char key) {
  if (key == 'w') {
    runX(X_PLUS_DIR);     // X+
  }
  else if (key == 's') {
    runX(X_MINUS_DIR);    // X-
  }
  else if (key == 'q') {
    runY(Y_PLUS_DIR);     // Y+
  }
  else if (key == 'e') {
    runY(Y_MINUS_DIR);    // Y-
  }
  else if (key == 'a') {
    runZ(Z_PLUS_DIR);     // Z+
  }
  else if (key == 'd') {
    runZ(Z_MINUS_DIR);    // Z-
  }
  else if (key == 'x' || key == ' ') {
    stopAll();
  }
}

/* ================= SETUP ================= */
void setup() {
Serial.begin(115200);      // xem debug trên máy tính
  espSerial.begin(9600);     // nhận lệnh từ ESP32-C3

  pinMode(X_STEP, OUTPUT);
  pinMode(Y_STEP, OUTPUT);
  pinMode(Z_STEP, OUTPUT);

  pinMode(X_DIR, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Z_DIR, OUTPUT);

  pinMode(ENABLE_PIN, OUTPUT);

  digitalWrite(ENABLE_PIN, LOW);   // bật toàn bộ driver

  digitalWrite(X_STEP, LOW);
  digitalWrite(Y_STEP, LOW);
  digitalWrite(Z_STEP, LOW);

  stopAll();

  Serial.println("UNO READY");
  Serial.println("Waiting command from ESP32-C3...");
}

/* ================= LOOP ================= */
void loop() {
  // Nhận lệnh từ ESP32-C3
  if (espSerial.available() > 0) {
    char key = espSerial.read();
    handleCommand(key);
  }

  // Có thể test trực tiếp bằng Serial Monitor của Uno
  if (Serial.available() > 0) {
    char key = Serial.read();
    handleCommand(key);
  }

  // Tạo xung liên tục cho motor đang chạy
  unsigned long now = micros();

  if (xRun && now - lastXStep >= STEP_INTERVAL_US) {
    lastXStep = now;
    stepMotor(X_STEP);
  }

  if (yRun && now - lastYStep >= STEP_INTERVAL_US) {
    lastYStep = now;
    stepMotor(Y_STEP);
  }

  if (zRun && now - lastZStep >= STEP_INTERVAL_US) {
    lastZStep = now;
    stepMotor(Z_STEP);
  }
}