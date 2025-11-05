/*
SPEED 1: 1000
SPEED 2: 800
SPEED 3: 600
SPEED 4: 400
SPEED 5: 200
*/

#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

const int forward_led = 6;
const int backward_led = 5;

unsigned long previousMillis = 0;
long interval = 1000; //default speed 1

int speed_interval = 1; //speed 1

String inputString = "";
bool stringComplete = false;

bool blinkState = false;

bool forwardState = false;
bool backwardState = false;
unsigned long previousDistance = 0;
const long distanceInterval = 10;
unsigned long distance = 0;
unsigned long maxDistance = 0;
unsigned long lastDistUpdate = 0;   // separate timer for distance


enum Movement {STOPPED, FORWARD, BACKWARD};
Movement movement = STOPPED;

const int RXPin = 2, TXPin = 3;
const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

bool warnNoGPS = false;

void setup() {
  pinMode(forward_led, OUTPUT);
  digitalWrite(forward_led, LOW);

  pinMode(backward_led, OUTPUT);
  digitalWrite(backward_led, LOW);

  Serial.begin(9600);
  ss.begin(GPSBaud);
  inputString.reserve(200);
}

void loop() {
  readSerial();

  if (stringComplete) {
    processSerial(inputString);
    inputString = "";
    stringComplete = false;
  }

  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      if (gps.location.isUpdated() && gps.location.isValid()) {
        Serial.print(F("GPSLAT:"));
        Serial.println(gps.location.lat(), 6);
        Serial.print(F("GPSLONG:"));
        Serial.println(gps.location.lng(), 6);
      }
    }
  }


  unsigned long now = millis();
  if (now - previousMillis >= (unsigned long)interval) {
    previousMillis = now;
    
    blinkState = !blinkState;

    switch (movement) {
      case FORWARD:
        digitalWrite(forward_led,  blinkState ? HIGH : LOW);
        digitalWrite(backward_led, LOW);
        forwardState = true;
        backwardState = false;
        break;
      case BACKWARD:
        digitalWrite(forward_led,  LOW);
        digitalWrite(backward_led, blinkState ? HIGH : LOW);
        forwardState = false;
        backwardState = true;
        break;
      case STOPPED:
      default:
        digitalWrite(forward_led,  LOW);
        digitalWrite(backward_led, LOW);
        forwardState = false;
        backwardState = false;
        break;
    }
  }

    if (lastDistUpdate == 0) lastDistUpdate = now;
unsigned long dt = now - lastDistUpdate;  // milliseconds since last update

if (dt > 0) {
  if (movement == FORWARD) {
    unsigned long next = distance + dt;                 // 1 ms = 1 mm
    if (maxDistance > 0 && next > maxDistance) next = maxDistance;
    distance = next;
  } else if (movement == BACKWARD) {
    long next = (long)distance - (long)dt;
    if (next < 0) next = 0;
    distance = (unsigned long)next;
  }
  lastDistUpdate = now;

  // Auto-stop when reaching limits
if (movement == FORWARD && maxDistance > 0 && distance >= maxDistance) {
  distance = maxDistance;             // clamp exactly
  handelMovement("STOPPED");          // stop movement + LEDs
}

if (movement == BACKWARD && distance <= 0) {
  distance = 0;                       // clamp exactly
  handelMovement("STOPPED");          // stop at min distance too
}


/* ----- TELEMETRY (rate-limit prints) ----- */
static unsigned long lastPrint = 0;
if (now - lastPrint >= 100) {  // 10 Hz
  lastPrint = now;
  Serial.print(F("DISTANCE:")); Serial.println(distance);       // mm
  Serial.print(F("MAXDIST:"));  Serial.println(maxDistance);    // mm
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
  else if (key == "LENGTH"){
    handelMaxDistance(value);
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

void handelMaxDistance(String value){
  value.trim();
  float m = value.toFloat();                 // accept decimals like 12.5
  if (m < 0) m = 0;
  maxDistance = (unsigned long)(m * 1000.0); // metres -> mm
  Serial.print(F("MAXDIST_SET:"));
  Serial.println(maxDistance);
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
