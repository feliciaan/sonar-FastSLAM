#include <ZumoMotors.h>

#include <SoftwareSerial.h>

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

#define BLUETOOTH_TXD 4
#define BLUETOOTH_RXD 5


#define SPEED 300
#define LEFT_SUM (-35) // left is a bit slower, we adjust here
#define OUT_OF_RANGE 9999

// time out in milli-secs
#define TIME_OUT 400
#define TIME_OUT_MuS (TIME_OUT*1000)

#define DEBUG 0

ZumoMotors motors;
SoftwareSerial bluetooth(BLUETOOTH_TXD, BLUETOOTH_RXD); // RX, TX


int last_order = 'A';

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

  motors.flipLeftMotor(1);
  motors.flipRightMotor(1);

  pinMode(LED, OUTPUT);
  Serial.println("Setup done");
  bluetooth.begin(9600);
  bluetooth.println("Setup done! ");
 // test_motors();
  digitalWrite(LED, HIGH);
  delay(1000);
  last_order = 'A';
  digitalWrite(LED, LOW);

}

void test_motors(){
  Serial.println("Motor test in one sec!");
  delay(500);
  Serial.println("HURRY! DISCONNECT ME");
  delay(500);
  forward();
  delay(5000);
  backward();
  delay(5000);
  halt();
}

long read_distance(const int trigPin, const int echoPin) {
  long duration, distance;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH, TIME_OUT_MuS); // TIME_OUT is in millis, function excpects micro's
  if (duration == 0) {
    // we time-outed
    distance = OUT_OF_RANGE;
  } else {
    distance = (duration / 2) / 29.1;

  }
  return distance;
}

void forward() {
  moveAround(SPEED, SPEED);
}

void backward() {
  moveAround(-SPEED, -SPEED);
}

void turn_left() {
  moveAround(-SPEED, SPEED);
}

void turn_right() {
  moveAround(SPEED, -SPEED);
}

void halt() {
  moveAround(0, 0);
}

int old_left, old_right;
long last_millis;
void moveAround(int left, int right) {
  long new_millis;
  int correction = LEFT_SUM;
  if (left < 0) {
    correction = -correction;
  } else if (left == 0) {
    correction = 0;
  }
  if (old_left != left || old_right != right) {
    bluetooth.print("el:");
    bluetooth.print(left);
    bluetooth.print("er");
    bluetooth.print(right);
    bluetooth.print("cor");
    bluetooth.print(correction);
    bluetooth.print("t:");


    Serial.print("el:");
    Serial.print(left);
    Serial.print("er");
    Serial.print(right);
    Serial.print("cor bij links: +");
    Serial.print(correction);
    Serial.print("t:");


    new_millis = millis();
    bluetooth.println(new_millis - last_millis);
    Serial.println(new_millis - last_millis);



    last_millis = new_millis;

    old_left = left;
    old_right = right;
  }

  motors.setLeftSpeed(left + correction);
  motors.setRightSpeed(right);
}


void auto_move(const int left, const int front, const int right) {
  int spd;
  if (front == OUT_OF_RANGE && right == OUT_OF_RANGE && left == OUT_OF_RANGE) {
    Serial.println("SENSORS LOST!");
    digitalWrite(LED, HIGH);

  } else if (front < 40) {
    // rotate a few degrees
    Serial.println("TURNING");

    if (right < left) {
      turn_left();
    } else {
      turn_right();
    }
  } else {
    digitalWrite(LED, LOW);
    forward();
  }

}


// receives orders from bluetooth
// Returns '_' if no order received
char receive_orders() {
  char rd;
  if (Serial.available()) {
    return Serial.read();
  }
  if (bluetooth.available()) {
    rd = bluetooth.read();
    Serial.print("Received: ");
    Serial.println(rd);
    return rd;
  }
  return '_';

}


void loop() {
  long front, right, left;
  char new_order;

  left = read_distance(SENSL_TRIG, SENSL_ECHO);
  front = read_distance(SENSF_TRIG, SENSF_ECHO);
  right  = read_distance(SENSR_TRIG, SENSR_ECHO);

  if (1) {
    bluetooth.print("L");
    bluetooth.print(left);


    bluetooth.print("F");
    bluetooth.print(front);

    bluetooth.print("R");
    bluetooth.println(right);
  }

  if (DEBUG) {
    Serial.print("L: ");
    Serial.print(left);
    Serial.print(" cm ");
    Serial.print("F: ");
    Serial.print(front);
    Serial.print(" cm ");
    Serial.print("R: ");
    Serial.print(right);
    Serial.println(" cm");
  }

  new_order = receive_orders();
  if (new_order != '_') {
    last_order = new_order;
  } else if (last_order != 'A') {
    last_order = 'S';
  }

  if (last_order == 'A') {
    auto_move(left, front, right);
  } else if (last_order == 'S') {
    halt();
  } else if (last_order == 'z') {
    if (front > 15) {
      forward();
    } else {
      Serial.println("Emergency break! Something is in the way");
    }
  } else if (last_order == 's') {
    backward();
  } else if (last_order == 'd') {
    turn_left();
  } else if (last_order == 'q') {
    turn_right();
  }


}

