#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

// GPS module connections to Arduino Nano
// Connect GPS TX → Arduino pin 3 (RX)
// Connect GPS RX → Arduino pin 2 (TX)
static const int RXPin = 3, TXPin = 2;
static const uint32_t GPSBaud = 9600;

// Create GPS and serial objects
TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

void setup() {
  // Begin serial communication for the monitor
  Serial.begin(9600);
  while (!Serial); // Wait for Serial to open on Nano (especially if using native USB versions)

  // Begin serial communication with the GPS module
  ss.begin(GPSBaud);

  // Serial.println(F("TinyGPS++ Example for Arduino Nano"));
  // Serial.println(F("Ensure GPS TX → D3 and GPS RX → D2"));
  // Serial.println(F("Waiting for GPS data...\n"));
}

void loop() {
  // Continuously read data from GPS
  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      displayInfo();
    }
  }

  // If after 5 seconds no GPS data has been processed, alert the user
  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println(F("No GPS detected: check wiring and baud rate."));
    while (true);
  }
}

void displayInfo() {
  Serial.println(F("------ GPS Data ------"));

  // Location data
  if (gps.location.isValid()) {
    Serial.print(F("Latitude: "));
    Serial.println(gps.location.lat(), 6);
    Serial.print(F("Longitude: "));
    Serial.println(gps.location.lng(), 6);
    Serial.print(F("Google Maps: https://www.google.com/maps/place/"));
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.println(gps.location.lng(), 6);
  } else {
    Serial.println(F("Location: INVALID"));
  }

  // Date
  if (gps.date.isValid()) {
    Serial.print(F("Date: "));
    Serial.print(gps.date.month());
    Serial.print(F("/"));
    Serial.print(gps.date.day());
    Serial.print(F("/"));
    Serial.println(gps.date.year());
  } else {
    Serial.println(F("Date: INVALID"));
  }

  // Time
  if (gps.time.isValid()) {
    Serial.print(F("Time (UTC): "));
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour());
    Serial.print(F(":"));
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute());
    Serial.print(F(":"));
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.println(gps.time.second());
  } else {
    Serial.println(F("Time: INVALID"));
  }

  Serial.println();
}
