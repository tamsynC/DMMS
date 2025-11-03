// #include <TinyGPSPlus.h>
// #include <SoftwareSerial.h>

// // GPS module connections to Arduino Nano
// // Connect GPS TX → Arduino pin 3 (RX)
// // Connect GPS RX → Arduino pin 2 (TX)
// static const int RXPin = 2, TXPin = 3;
// static const uint32_t GPSBaud = 9600;

// // Create GPS and serial objects
// TinyGPSPlus gps;
// SoftwareSerial ss(RXPin, TXPin);
// void setup() {
//   // Begin serial communication for the monitor
//   Serial.begin(9600);
//   while (!Serial); // Wait for Serial to open on Nano (especially if using native USB versions)

//   // Begin serial communication with the GPS module
//   ss.begin(GPSBaud);
//  // Serial.println(F("TinyGPS++ Example for Arduino Nano"));
//   // Serial.println(F("Ensure GPS TX → D3 and GPS RX → D2"));
//   // Serial.println(F("Waiting for GPS data...\n"));
// }
// void loop() {
//   // Continuously read data from GPS
//   while (ss.available() > 0) {
//     if (gps.encode(ss.read())) {
//       displayInfo();
//     }
//   }
//   // If after 5 seconds no GPS data has been processed, alert the user
//   if (millis() > 5000 && gps.charsProcessed() < 10) {
//     Serial.println(F("No GPS detected: check wiring and baud rate."));
//     while (true);
//   }
// }
// void displayInfo() {
//   Serial.println(F("------ GPS Data ------"));
//  // Location data
//   if (gps.location.isValid()) {
//     Serial.print(F("Latitude: "));
//     Serial.println(gps.location.lat(), 6);
//     Serial.print(F("Longitude: "));
//     Serial.println(gps.location.lng(), 6);
//     Serial.print(F("Google Maps: https://www.google.com/maps/place/"));
//     Serial.print(gps.location.lat(), 6);
//     Serial.print(F(","));
//     Serial.println(gps.location.lng(), 6);
//   } else {
//    Serial.println(F("Location: INVALID"));
//   }

//   // Date
//   if (gps.date.isValid()) {
//     Serial.print(F("Date: "));
//     Serial.print(gps.date.month());
//     Serial.print(F("/"));
//     Serial.print(gps.date.day());
//     Serial.print(F("/"));
//     Serial.println(gps.date.year());
//   } else {
//     Serial.println(F("Date: INVALID"));
//   }
//   // Time
//   if (gps.time.isValid()) {
//     Serial.print(F("Time (UTC): "));
//     if (gps.time.hour() < 10) Serial.print(F("0"));
//     Serial.print(gps.time.hour());
//     Serial.print(F(":"));
//     if (gps.time.minute() < 10) Serial.print(F("0"));
//     Serial.print(gps.time.minute());
//     Serial.print(F(":"));
//     if (gps.time.second() < 10) Serial.print(F("0"));
//     Serial.println(gps.time.second());
//   } else {
//     Serial.println(F("Time: INVALID"));
//   }

//   Serial.println();
// }



#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

// ---------- GPS wiring (Arduino Nano) ----------
// GPS TX -> Arduino D3 (RX), GPS RX -> Arduino D2 (TX)
static const int RXPin = 3, TXPin = 2;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

// ---------- LED pins ----------
const int LED_A = 6;
const int LED_B = 5;

// ---------- Serial cmd buffer ----------
String inputString = "";
bool stringComplete = false;

// ---------- Distance counter ----------
unsigned long millisCount = 0;
bool ledAState = false;
bool ledBState = false;

unsigned long previousMillis = 0;
const unsigned long interval = 100; // 100 ms

// ---------- GPS warning control ----------
bool warnedNoGPS = false;
unsigned long startMillis = 0;

void setup() {
  pinMode(LED_A, OUTPUT);
  pinMode(LED_B, OUTPUT);
  digitalWrite(LED_A, LOW);
  digitalWrite(LED_B, LOW);

 Serial.begin(9600);
  ss.begin(GPSBaud);

  inputString.reserve(200);
  startMillis = millis();
}

void loop() {
  // --- Read GPS bytes into TinyGPS++ ---
  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      // When a full GPS sentence was parsed, push an update if we have new location
      if (gps.location.isUpdated() && gps.location.isValid()) {
        Serial.print(F("GPS:"));
        Serial.print(gps.location.lat(), 6);
        Serial.print(F(","));
        Serial.println(gps.location.lng(), 6);
      }
    }
  }

  // Warn once if no GPS after 5 s (don't block)
  if (!warnedNoGPS && (millis() - startMillis > 5000) && gps.charsProcessed() < 10) {
    Serial.println(F("GPS:INVALID"));
    warnedNoGPS = true;
 }

  // --- 100 ms ticker: update distance and publish COUNT ---
unsigned long currentMillis = millis();
if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (ledAState) millisCount += interval;          // forward adds distance
    if (ledBState && millisCount >= interval) millisCount -= interval; // backward subtracts

    Serial.print(F("COUNT:"));
    Serial.println(millisCount);
 }

  // --- Process serial commands from Python (F0/F1/R0/R1) ---
  serialCommandReader();
  if (stringComplete) {
    if (inputString == "F0\n") { digitalWrite(LED_A, LOW);  ledAState = false; }
    else if (inputString == "F1\n") { digitalWrite(LED_A, HIGH); ledAState = true; }
    else if (inputString == "R0\n") { digitalWrite(LED_B, LOW);  ledBState = false; }
    else if (inputString == "R1\n") { digitalWrite(LED_B, HIGH); ledBState = true; }

    inputString = "";
    stringComplete = false;
  }
}

void serialCommandReader() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
   inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
