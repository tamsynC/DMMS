// CNC-style serial stepper control with A4988
// Commands from serial: F1 (forward on), F0 (forward off), R1 (reverse on), R0 (reverse off)

int xStep = 5;
int xDir  = 2;
int yStep = 6;
int yDir  = 3;
int enablePin = 8;  // CNC shield enable pin (LOW = enabled)

bool forwardOn = false;
bool reverseOn = false;

void setup() {
  pinMode(xStep, OUTPUT);
  pinMode(xDir, OUTPUT);
  pinMode(yStep, OUTPUT);
  pinMode(yDir, OUTPUT);
  pinMode(enablePin, OUTPUT);

  digitalWrite(enablePin, LOW); // enable drivers
  Serial.begin(9600);
  Serial.println("Stepper control ready. Send F1/F0/R1/R0");
}

void loop() {
  // --- Check for serial command ---
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();  // removes newline and spaces

    if (cmd == "F1") {
      forwardOn = true;
      reverseOn = false;
      digitalWrite(xDir, HIGH);
      digitalWrite(yDir, HIGH);
      Serial.println("Forward ON");
    }
    else if (cmd == "F0") {
      forwardOn = false;
      Serial.println("Forward OFF");
    }
    else if (cmd == "R1") {
      reverseOn = true;
      forwardOn = false;
      digitalWrite(xDir, LOW);
      digitalWrite(yDir, LOW);
      Serial.println("Reverse ON");
    }
    else if (cmd == "R0") {
      reverseOn = false;
      Serial.println("Reverse OFF");
    }
    else {
      Serial.println("Unknown command");
    }
  }

  // --- Move steppers if active ---
  if (forwardOn || reverseOn) {
    digitalWrite(xStep, HIGH);
    digitalWrite(yStep, HIGH);
    delayMicroseconds(700);  // speed control
    digitalWrite(xStep, LOW);
    digitalWrite(yStep, LOW);
    delayMicroseconds(700);
  }
}
