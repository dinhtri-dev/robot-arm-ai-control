#include <Arduino.h>

/* ================= CNC SHIELD V3 PIN ================= */
#define X_STEP 2
#define Y_STEP 3
#define Z_STEP 4

#define X_DIR 5
#define Y_DIR 6
#define Z_DIR 7

#define ENABLE_PIN 8   // EN của CNC Shield V3

/* ================= SETTING ================= */
// Motor NEMA17 thường: 200 step / vòng nếu full-step
// Nếu cắm jumper vi bước 1/16 trên CNC Shield thì dùng 3200
#define STEPS_PER_REV 200

// Tốc độ quay: số micro giây giữa các xung
// Số càng nhỏ motor quay càng nhanh
#define STEP_DELAY_US 800

void moveOneRev(int stepPin, int dirPin, bool dir) {
  digitalWrite(dirPin, dir);

  for (long i = 0; i < STEPS_PER_REV; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(STEP_DELAY_US);

    digitalWrite(stepPin, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(X_STEP, OUTPUT);
  pinMode(Y_STEP, OUTPUT);
  pinMode(Z_STEP, OUTPUT);

  pinMode(X_DIR, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Z_DIR, OUTPUT);

  pinMode(ENABLE_PIN, OUTPUT);

  // EN active LOW: kéo LOW để bật driver
  digitalWrite(ENABLE_PIN, LOW);

  Serial.println("=== CNC Shield V3 Stepper Test ===");
  Serial.println("Gui q: X quay 1 vong");
  Serial.println("Gui w: Y quay 1 vong");
  Serial.println("Gui e: Z quay 1 vong");
}

void loop() {
  if (Serial.available() > 0) {
    char key = Serial.read();

    if (key == 'q') {
      Serial.println("X quay 1 vong");
      moveOneRev(X_STEP, X_DIR, HIGH);
      Serial.println("X done");
    }

    else if (key == 'w') {
      Serial.println("Y quay 1 vong");
      moveOneRev(Y_STEP, Y_DIR, HIGH);
      Serial.println("Y done");
    }

    else if (key == 'e') {
      Serial.println("Z quay 1 vong");
      moveOneRev(Z_STEP, Z_DIR, HIGH);
      Serial.println("Z done");
    }
  }
}