const int LED_A = 6;
const int LED_B = 5;

String inputString = "";
bool stringComplete = false;

void setup() {
  pinMode(LED_A, OUTPUT);
  pinMode(LED_B, OUTPUT);

  digitalWrite(LED_A, LOW);
  digitalWrite(LED_B, LOW);

  Serial.begin(9600);

  inputString.reserve(200);
}

void loop() {
  
  serialLED();

  if(stringComplete) {
    Serial.print(inputString);

    /*
    F0 = forward FALSE
    F1 = forward TRUE

    R0 = reverse FALSE
    R1 = reverse TRUE
    */

    if(inputString == "F0\n") {digitalWrite(LED_A, LOW);}
    else if(inputString == "F1\n") {digitalWrite(LED_A, HIGH);}
    else if(inputString == "R0\n") {digitalWrite(LED_B, LOW);}
    else if(inputString == "R1\n") {digitalWrite(LED_B, HIGH);}

    inputString = "";
    stringComplete = false;
  }
}

void serialLED() {
  while(Serial.available()){
    char inChar = (char)Serial.read();

    inputString += inChar;\
    
    if(inChar == '\n') {
      stringComplete = true;
    }
    }
  }

