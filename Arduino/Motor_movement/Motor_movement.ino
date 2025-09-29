// CNC-style serial stepper control with A4988
// Commands: F1 (forward on), F0 (forward stop), R1 (reverse on), R0 (reverse stop)

 int xStep = 2;
 int xDir  = 5;
 int yStep = 3;
 int yDir  = 6;

bool forwardOn = false;
bool reverseOn = false;

void setup() {
  pinMode(xStep, OUTPUT);
  pinMode(xDir, OUTPUT);
  pinMode(yStep, OUTPUT);
  pinMode(yDir, OUTPUT);

  Serial.begin(9600);  // must match Python BAUD rate
}

void loop() {
  // Check for serial command
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

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
  }

  // Move steppers if active
  if (forwardOn || reverseOn) {
    digitalWrite(xStep, HIGH);
    digitalWrite(yStep, HIGH);
    delayMicroseconds(500);  // Adjust speed
    digitalWrite(xStep, LOW);
    digitalWrite(yStep, LOW);
    delayMicroseconds(500);
  }
}