#include <ZumoMotors.h>
  
// pin layout:

#define RED error
#define BLUE A3
#define GREEN A4 
#define ORANGE A5
#define YELLOW A1
#define BLACK error
//EMPTY
#define GRAY A4// yeah, we reuse a pin. As long as it's a trigger pin, we'll be
#define WHITE A2  
//EMPTY

#define LED 13

#define SENSL_TRIG GREEN
#define SENSL_ECHO BLUE

#define SENSF_TRIG YELLOW
#define SENSF_ECHO ORANGE

#define SENSR_TRIG GRAY
#define SENSR_ECHO WHITE

// time out in milli-secs
#define TIME_OUT 400
#define TIME_OUT_MuS (TIME_OUT*1000)

ZumoMotors motors;

void setup() {
  digitalWrite(LED, HIGH);
  Serial.begin (9600);
  pinMode(SENSL_TRIG, OUTPUT);
  pinMode(SENSL_ECHO, INPUT);
  pinMode(SENSF_TRIG, OUTPUT);
  pinMode(SENSF_ECHO, INPUT);
  pinMode(SENSR_TRIG, OUTPUT);
  pinMode(SENSR_ECHO, INPUT);
  
  digitalWrite(SENSL_TRIG, LOW);
  digitalWrite(SENSF_TRIG, LOW);
  digitalWrite(SENSR_TRIG, LOW);
  
  
  pinMode(LED, OUTPUT); 
  Serial.println("Setup done");
}

long read_distance(const int trigPin, const int echoPin){
  long duration, distance;  
  
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10); 
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH, TIME_OUT_MuS); // TIME_OUT is in millis, function excpects micro's
  if(duration == 0){
    // we time-outed
    distance = 99999;
  }else{
    distance = (duration/2) / 29.1;
    
  }
  return distance;
}


int led_status = HIGH;

void loop() {
  long front, right, left;


  left = read_distance(SENSL_TRIG, SENSL_ECHO);
  Serial.print("L: ");
  Serial.print(left);
  Serial.print(" cm ");
 
  front = read_distance(SENSF_TRIG, SENSF_ECHO);
  Serial.print("F: ");
  Serial.print(front);
  Serial.print(" cm ");
  
  right  = read_distance(SENSR_TRIG, SENSR_ECHO);
  Serial.print("R: ");
  Serial.print(right);
  Serial.println(" cm");

  
  
  
  motors.setLeftSpeed(400);
  
  
  
  
  
  if(led_status == HIGH){
    led_status = LOW;
  }else{
    led_status = HIGH;
  }
  digitalWrite(LED, led_status);
  


  delay(500);
} 



