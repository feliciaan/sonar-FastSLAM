#import <SoftwareSerial.h>

#define BLUETOOTH_TXD 4
#define BLUETOOTH_RXD 5
SoftwareSerial bluetooth(BLUETOOTH_TXD, BLUETOOTH_RXD); // RX, TX

void setup(){
 Serial.begin (9600);
 
 Serial.println("Hi"); 
 bluetooth.begin(38400);
 bluetooth.println("Hello, world?");
}

void loop(){
 if (bluetooth.available()) {
    Serial.write(bluetooth.read());
  }
  if (Serial.available()) {
    bluetooth.write(Serial.read());
  }
}



