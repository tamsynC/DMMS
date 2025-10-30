/*
SPEED 1: 1000
SPEED 2: 800
SPEED 3: 600
SPEED 4: 400
SPEED 5: 200
*/

const int forward_led = 6;
const int backward_led = 5;

unsigned long previousMillis = 0;
long interval = 1000; //default speed 1

int speed_interval = 1; //speed 1

String inputString = "";
bool stringComplete = false;

bool blinkState = false;

enum Movement {STOPPED, FORWARD, BACKWARD};
Movement movement = STOPPED;


void setup() {
  pinMode(forward_led, OUTPUT);
  digitalWrite(forward_led, LOW);

  pinMode(backward_led, OUTPUT);
  digitalWrite(backward_led, LOW);

  Serial.begin(9600);
  inputString.reserve(200);
}

void loop() {
  readSerial();

  if (stringComplete) {
    processSerial(inputString);
    inputString = "";
    stringComplete = false;
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= (unsigned long)interval) {
    previousMillis = currentMillis;
    
    blinkState = !blinkState;

    switch (movement) {
      case FORWARD:
        digitalWrite(forward_led,  blinkState ? HIGH : LOW);
        digitalWrite(backward_led, LOW);
        break;
      case BACKWARD:
        digitalWrite(forward_led,  LOW);
        digitalWrite(backward_led, blinkState ? HIGH : LOW);
        break;
      case STOPPED:
      default:
        digitalWrite(forward_led,  LOW);
        digitalWrite(backward_led, LOW);
        break;
    }
  }
}

void processSerial(String cmd){
  cmd.trim();
  
  int colon = cmd.indexOf(':');
  String key, value;

  key = cmd.substring(0, colon);
  value = cmd.substring(colon + 1);

  key.trim();
  value.trim();

  key.toUpperCase();

  if (key == "SPEED") {
    handelSpeed(value);
  }
  else if (key == "MOVEMENT"){
    handelMovement(value);
  }
}

void handelMovement(String value){
  value.trim();
  value.toUpperCase();

  if (value == "FORWARD"){
    movement = FORWARD;
  }
  else if (value == "BACKWARD"){
    movement = BACKWARD;
  }
  else if (value == "STOPPED"){
    movement = STOPPED;
  }

  blinkState = true;
  previousMillis = millis();

  switch (movement) {
    case FORWARD:
      digitalWrite(forward_led,  HIGH);
      digitalWrite(backward_led, LOW);
      break;
    case BACKWARD:
      digitalWrite(forward_led,  LOW);
      digitalWrite(backward_led, HIGH);
      break;
    case STOPPED:
      digitalWrite(forward_led,  LOW);
      digitalWrite(backward_led, LOW);
      break;
  }
}

void handelSpeed(String value) {
  int level = value.toInt();

  switch(level){
    case 1:
      interval = 1000;
      break;
    case 2:
      interval = 800;
      break;
    case 3:
      interval = 600;
      break;
    case 4:
      interval = 400;
      break;
    case 5:
      interval = 200;
      break;
    default:
      return;
  }
}

void readSerial(){
  while (Serial.available()){
    char inChar = (char)Serial.read();
    inputString += inChar;

    if (inChar == '\n'){
      stringComplete = true;
    }
  }
}
