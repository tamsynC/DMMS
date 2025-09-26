// const int LED_A = 6;
// const int LED_B = 5;

// String inputString = "";
// bool stringComplete = false;

// unsigned long millisCount = 0;

// bool ledAState = false;  
// bool ledBState = false;  

// unsigned long ledAStart = 0;  
// unsigned long ledBStart = 0; 

// void setup() {
//   pinMode(LED_A, OUTPUT);
//   pinMode(LED_B, OUTPUT);

//   digitalWrite(LED_A, LOW);
//   digitalWrite(LED_B, LOW);

//   Serial.begin(9600);

//   inputString.reserve(200);
// }

// void loop() {
  
//   serialLED();

//   if(stringComplete) {
//     // Serial.print(inputString);

//     /*
//     F0 = forward FALSE
//     F1 = forward TRUE

//     R0 = reverse FALSE
//     R1 = reverse TRUE
//     */

//     if(inputString == "F0\n") {

//       if(ledAState){
//         unsigned long duration = millis() - ledAStart;
//         millisCount += duration;
//       }
//       digitalWrite(LED_A, LOW);
//       ledAState = false;
//     }

//     else if(inputString == "F1\n") {
      
//       ledAStart = millis();
//       digitalWrite(LED_A, HIGH);
//       ledAState = true;
//     }

//     else if(inputString == "R0\n") {

//       if(ledBState) {
//         unsigned long duration = millis() - ledBStart;
//         if(millisCount >= duration){
//           millisCount -= duration;
//         }else{
//           millisCount = 0;
//         }
//       }
//       digitalWrite(LED_B, LOW);
//       ledBState = false;
//     }

//     else if(inputString == "R1\n") {
//       ledBStart = millis();
//       digitalWrite(LED_B, HIGH);
//       ledBState = true;
//     }

//     Serial.print("COUNT: ");
//     Serial.println(millisCount);

//     inputString = "";
//     stringComplete = false;
//   }
// }

// void serialLED() {
//   while(Serial.available()){
//     char inChar = (char)Serial.read();

//     inputString += inChar;
    
//     if(inChar == '\n') {
//       stringComplete = true;
//     }
//     }
//   }

const int LED_A = 6;
const int LED_B = 5;

String inputString = "";
bool stringComplete = false;

unsigned long millisCount = 0;

bool ledAState = false;  
bool ledBState = false;  

unsigned long previousMillis = 0;  // for 100 ms updates
const unsigned long interval = 100; // update interval

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

  unsigned long currentMillis = millis();


  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (ledAState) millisCount += interval;
    if (ledBState && millisCount >= interval) millisCount -= interval;

    Serial.print("COUNT:");
    Serial.println(millisCount);
    // Send count to Python
    Serial.print("COUNT:");
    Serial.println(millisCount);
  }


  if (stringComplete) {
    if (inputString == "F0\n") {
      digitalWrite(LED_A, LOW);
      ledAState = false;
    }
    else if (inputString == "F1\n") {
      digitalWrite(LED_A, HIGH);
      ledAState = true;
    }
    else if (inputString == "R0\n") {
      digitalWrite(LED_B, LOW);
      ledBState = false;
    }
    else if (inputString == "R1\n") {
      digitalWrite(LED_B, HIGH);
      ledBState = true;
    }

    inputString = "";
    stringComplete = false;
  }
}

void serialLED() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;

    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}


