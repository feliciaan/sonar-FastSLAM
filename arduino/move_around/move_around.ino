#include <ZumoMotors.h>

#include <SoftwareSerial.h>

/********************* pin -> color layout and other pins *******************/
/*** On the jumper ***/

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


/*** Misc other devices ***/
#define LED 13  // led on the Zumo and arduino, goes on when no input is in range

#define BLUETOOTH_TXD 4
#define BLUETOOTH_RXD 5

/********************* color -> sensor layout: ******************************/
#define SENSL_TRIG GREEN
#define SENSL_ECHO BLUE

#define SENSF_TRIG YELLOW
#define SENSF_ECHO ORANGE

#define SENSR_TRIG GRAY
#define SENSR_ECHO WHITE


/********************* motor speeds ******************************************/
#define SPEED 300
#define LEFT_SUM (-35) // left is a bit slower, we adjust here


/********************* Sensor settings ***************************************/

#define OUT_OF_RANGE 9999
// time out in milli-secs
#define TIME_OUT 400
#define TIME_OUT_MuS (TIME_OUT*1000)

/********************* Enable/disable output/input sending ********************/
#define SERIAL_SENSOR_UPDATES 0
#define SERIAL_MOTOR_UPDATES 1
#define BLUETOOTH_SENSOR_UPDATES 1
#define BLUETOOTH_MOTOR_UPDATES 1

// disable if someone sends annoying commands while debugging over cable
#define BLUETOOTH_ACCEPT_ORDERS 1

/********************* Variables ***************************/

ZumoMotors motors;
SoftwareSerial bluetooth(BLUETOOTH_TXD, BLUETOOTH_RXD); // RX, TX

int last_order; // what the loop executes


// we keep track of the speeds and report those, each time they change, we send this on to bluetooth
int old_left_speed, old_right_speed;
/* the last time motor speed changed. Millis is expressed using the 'millis()'-functions.
   We use this value as epoch and count both motor changes and measurements starting from this moment
*/
long last_motor_change_millis;

void setup() {
  int led_speed = 75;//speed of warning led
  digitalWrite(LED, HIGH);
  Serial.begin (9600);

  // init of sensors
  pinMode(SENSL_TRIG, OUTPUT);
  pinMode(SENSL_ECHO, INPUT);
  pinMode(SENSF_TRIG, OUTPUT);
  pinMode(SENSF_ECHO, INPUT);
  pinMode(SENSR_TRIG, OUTPUT);
  pinMode(SENSR_ECHO, INPUT);

  digitalWrite(SENSL_TRIG, LOW);
  digitalWrite(SENSF_TRIG, LOW);
  digitalWrite(SENSR_TRIG, LOW);

  // init of motors
  motors.flipLeftMotor(1);
  motors.flipRightMotor(1);

  pinMode(LED, OUTPUT);
  bluetooth.begin(9600);

  bluetooth.println("# Setup done! ");
  Serial.println("# Setup done");



  // a second of delay, to give time to disconnect cables etc...
  for (int i = 0; i < 1500; i += led_speed) {
    digitalWrite(LED, HIGH);
    delay(led_speed);
    digitalWrite(LED, LOW);
    delay(led_speed);
  }
  last_order = 'S';
  bluetooth.println("# Waiting for your command");
  Serial.println("# Waiting for your command");

}





/********************* Distance sensors *******************************************/

long read_distance_sensor(const int trigPin, const int echoPin) {
  long duration;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH, TIME_OUT_MuS); // TIME_OUT is in millis, function excpects micro's
  if (duration == 0) {
    // we time-outed, we return a lot of 9s
    return OUT_OF_RANGE;
  } else {
    return (duration / 2) / 29.1;
  }
}

/********************* Order reading and dispatch *******************************************/

/* Receives orders from bluetooth
 * Returns '_' if no order received
 */

char receive_orders() {
  char rd;
  if (Serial.available()) {
    return Serial.read();
  }
  if (bluetooth.available()) {
    rd = bluetooth.read();
    Serial.print("# Received: ");
    Serial.println(rd);
    return rd;
  }
  return '_';

}

void send_sensor_data(int left, int front, int right){
  if (BLUETOOTH_SENSOR_UPDATES) {
    bluetooth.print("L");
    bluetooth.print(left);
    bluetooth.print("F");
    bluetooth.print(front);
    bluetooth.print("R");
    bluetooth.print(right);
    bluetooth.print("t");
    bluetooth.println(millis() - last_motor_change_millis);
  }

  if (SERIAL_SENSOR_UPDATES) {
    Serial.print("L: ");
    Serial.print(left);
    Serial.print("cm\t");
    Serial.print("F: ");
    Serial.print(front);
    Serial.print("cm\t");
    Serial.print("R: ");
    Serial.print(right);
    Serial.println("cm");
  }
}




/********************* Motor control *******************************************/

inline void forward() {
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

void test_motors() {
  forward();
  delay(5000);
  backward();
  delay(5000);
  halt();
}

/**
   All motor changes should go through this method!
   It keeps track of the timing, resets it, sends motor updates to bluetooth and serial, ...
*/
void moveAround(int left, int right) {
  long new_millis;

  // correction factor on the left wheel
  int correction = LEFT_SUM;
  if (left < 0) {
    correction = -correction;
  } else if (left == 0) {
    correction = 0;
  }

  if (old_left_speed != left || old_right_speed != right) {
    new_millis = millis();

    if (BLUETOOTH_MOTOR_UPDATES) {
      bluetooth.print("el");
      bluetooth.print(left);
      bluetooth.print("er");
      bluetooth.print(right);
      bluetooth.print("cor");
      bluetooth.print(correction);
      bluetooth.print("t");
      bluetooth.println(new_millis - last_motor_change_millis);
    }

    if (SERIAL_MOTOR_UPDATES) {
      Serial.print("el");
      Serial.print(left);
      Serial.print("er");
      Serial.print(right);
      Serial.print("cor");
      Serial.print(correction);
      Serial.print("t");
      Serial.println(new_millis - last_motor_change_millis);
    }

    // reset the timing
    last_motor_change_millis = new_millis;

    old_left_speed = left;
    old_right_speed = right;
  }

  // actually run the motors
  motors.setLeftSpeed(left + correction);
  motors.setRightSpeed(right);

}


void auto_move(const int left, const int front, const int right) {
  int spd;
  if (front == OUT_OF_RANGE && right == OUT_OF_RANGE && left == OUT_OF_RANGE) {
    digitalWrite(LED, HIGH);

  } else if (front < 40) {
    // rotate a few degrees
    turn_left();

  } else {
    digitalWrite(LED, LOW);
    forward();
  }

}


/***************************************************************************************/
/********************************* Main Loop *******************************************/
/***************************************************************************************/


void loop() {
  long left, front, right;
  char new_order;

  left = read_distance_sensor(SENSL_TRIG, SENSL_ECHO);
  front = read_distance_sensor(SENSF_TRIG, SENSF_ECHO);
  right  = read_distance_sensor(SENSR_TRIG, SENSR_ECHO);

  send_sensor_data(left, front, right);

  new_order = receive_orders();
  if(new_order == '_') {
    // no order received this tick
    // the default order is 'halt', only if we are in auto mode, we continue auto mode
    if (last_order == 'A'){
      new_order = 'A';
    } 
  }
  last_order = new_order;

  switch(last_order){
    case 'A': auto_move(left, front, right);  break;
    case 'H': halt();                         break;
    case 'z': forward();                      break;
    case 's': backward();                     break;
    case 'd': turn_left();                    break;
    case 'q': turn_right();                   break;
    default : halt();
  }

}

