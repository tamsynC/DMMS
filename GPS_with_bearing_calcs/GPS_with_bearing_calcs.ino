#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

const int GPSRx = 2, GPSTx = 3;
const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial ss(GPSRx, GPSTx);

float lat = 0.0, lng = 0.0;
float latNorth = 0.0, longNorth = 0.0;
double bearing = 0.0;

void setup() {
  Serial.begin(9600);
  while(!Serial);
  ss.begin(GPSBaud);
}

void loop() {
  while(ss.available() > 0){
    if (gps.encode(ss.read())) {
      location();
    }
  }

  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println(F("No GPS detected: check wiring and baud rate."));
    while (true);
  }

}

void location() {
  if (gps.location.isValid()) {
    lat = gps.location.lat();
    lng = gps.location.lng();

    Serial.print("GPS: Lat: ");
    Serial.print(lat, 6);
    Serial.print("  Long: ");
    Serial.println(lng, 6);
  }
}



