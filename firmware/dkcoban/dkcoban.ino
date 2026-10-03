#include <Arduino.h>

/* ================= CNC SHIELD V3 PIN ================= */
#define X_STEP 2
#define Y_STEP 3
#define Z_STEP 4

#define X_DIR 5
#define Y_DIR 6
#define Z_DIR 7

#define ENABLE_PIN 8   // EN CNC Shield V3, LOW = bật driver

/* ================= SPEED SETTING ================= */
// Thời gian giữa 2 xung STEP
// Số càng nhỏ motor càng nhanh
// 2500us = tốc độ vừa, an toàn để test
#define STEP_INTERVAL_US 2500

// Độ rộng xung STEP
#define STEP_PULSE_US 5

/* ================= MOTOR STATE ================= */
bool xRun = false;
bool yRun = false;
bool zRun = false;

bool xDir = HIGH;
bool yDir = HIGH;
bool zDir = HIGH;

unsigned long lastXStep = 0;
unsigned long lastYStep = 0;
unsigned long lastZStep = 0;

/* ================= STEP FUNCTION ================= */
void stepMotor(uint8_t stepPin) {
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(STEP_PULSE_US);
  digitalWrite(stepPin, LOW);
}

/* ================= STOP ALL ================= */
void stopAll() {
  xRun = false;
  yRun = false;
  zRun = false;

  Serial.println("STOP ALL");
}

/* ================= SET ONLY ONE MOTOR RUN ================= */
void runOnlyX(bool dir) {
  xRun = true;
  yRun = false;
  zRun = false;

  xDir = dir;
  digitalWrite(X_DIR, xDir);

  Serial.println(dir == HIGH ? "X chieu +" : "X chieu -");
}

void runOnlyY(bool dir) {
  xRun = false;
  yRun = true;
  zRun = false;

  yDir = dir;
  digitalWrite(Y_DIR, yDir);

  Serial.println(dir == HIGH ? "Y chieu +" : "Y chieu -");
}

void runOnlyZ(bool dir) {
  xRun = false;
  yRun = false;
  zRun = true;

  zDir = dir;
  digitalWrite(Z_DIR, zDir);

  Serial.println(dir == HIGH ? "Z chieu +" : "Z chieu -");
}

/* ================= SETUP ================= */
void setup() {
  Serial.begin(115200);

  pinMode(X_STEP, OUTPUT);
  pinMode(Y_STEP, OUTPUT);
  pinMode(Z_STEP, OUTPUT);

  pinMode(X_DIR, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Z_DIR, OUTPUT);

  pinMode(ENABLE_PIN, OUTPUT);

  // Bật toàn bộ driver
  digitalWrite(ENABLE_PIN, LOW);

  digitalWrite(X_STEP, LOW);
  digitalWrite(Y_STEP, LOW);
  digitalWrite(Z_STEP, LOW);

  Serial.println("=== CNC Shield V3 Manual Jog Test ===");
  Serial.println("w: X+");
  Serial.println("s: X-");
  Serial.println("q: Y+");
  Serial.println("e: Y-");
  Serial.println("a: Z+");
  Serial.println("d: Z-");
  Serial.println("x hoac Space: STOP");
}

/* ================= LOOP ================= */
void loop() {
  /* ===== DOC LENH SERIAL ===== */
  if (Serial.available() > 0) {
    char key = Serial.read();

    if (key == 'w') {
      runOnlyX(HIGH);
    }
    else if (key == 's') {
      runOnlyX(LOW);
    }
    else if (key == 'q') {
      runOnlyY(HIGH);
    }
    else if (key == 'e') {
      runOnlyY(LOW);
    }
    else if (key == 'a') {
      runOnlyZ(HIGH);
    }
    else if (key == 'd') {
      runOnlyZ(LOW);
    }
    else if (key == 'x' || key == ' ') {
      stopAll();
    }
  }

  /* ===== TAO XUNG CHAY LIEN TUC ===== */
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