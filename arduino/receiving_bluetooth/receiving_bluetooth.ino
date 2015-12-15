
#define trigPin 5
#define echoPin 4
#define led 11
#define led2 10

String inputString = ""; //string that stores the incoming message
boolean stringComplete = false;

void setup()
{
  Serial.begin(9600); //set baud rate
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  // reserve 20 bytes for the inputString:
  inputString.reserve(20);
}

void loop()
{
  serialEvent(); //call the function
  
  // print the string when a newline arrives:
  if (stringComplete) {
    // Serial.println(inputString);
    
    // handle inputString
   if(inputString=="1\n"){
      long duration, distance;
      digitalWrite(trigPin, LOW);  // Added this line
      delayMicroseconds(2); // Added this line
      digitalWrite(trigPin, HIGH);
    //  delayMicroseconds(1000); - Removed this line
      delayMicroseconds(10); // Added this line
      digitalWrite(trigPin, LOW);
      duration = pulseIn(echoPin, HIGH);
     // Serial.println(duration);
      distance = (duration/2) / 29.1;
     // Serial.println(distance);
      if (distance >= 200 || distance <= 0){
        Serial.println("Out of range");
      }
      else {
        Serial.println(distance);
        //Serial.println(" cm");
      }
   }else{
     Serial.println('wrong command !');
   }
    
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}
/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}









    
