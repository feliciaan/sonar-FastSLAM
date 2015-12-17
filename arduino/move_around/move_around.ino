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
#define LEFT_SUM (-25) // left is a bit slower, we adjust here


/********************* Sensor settings ***************************************/

#define OUT_OF_RANGE 9999
// time out in milli-secs
#define TIME_OUT 400
#define TIME_OUT_MuS (TIME_OUT*1000)


/********************* Auto move settings *************************************/

// when the algorithm chooses a turning direction, it will keep this turning direction for 5secs, to prevent loops in cornersr
#define DIR_CHANGE_TIME 2500


/********************* Enable/disable output/input sending ********************/
// send each ... ms a sporadic sensor update
#define SPORADIC_SENSOR_UPDATE_INTERVAL 1000

#define SERIAL_SENSOR_UPDATES 0
#define SERIAL_SPORADIC_SENSOR_UPDATE 1
#define SERIAL_MOTOR_UPDATES 0
#define SERIAL_AUTO_DEBUG 0
#define SERIAL_SPORADIC_AUTO_UPDATE 1

#define BLUETOOTH_SENSOR_UPDATES 1
#define BLUETOOTH_SPORADIC_SENSOR_UPDATE 1
#define BLUETOOTH_MOTOR_UPDATES 1
#define BLUETOOTH_AUTO_DEBUG 0
#define BLUETOOTH_SPORADIC_AUTO_UPDATE 0

// disable if someone sends annoying commands while debugging over cable
#define BLUETOOTH_ACCEPT_ORDERS 1

#define START_MODE 't'

/********************* Variables ***************************/

#define LEFT 'l'
#define RIGHT 'r'

ZumoMotors motors;
SoftwareSerial bluetooth(BLUETOOTH_TXD, BLUETOOTH_RXD); // RX, TX

int last_order; // what the loop executes


// we keep track of the speeds and report those, each time they change, we send this on to bluetooth
int old_left_speed, old_right_speed;
long last_update_time_serial;
long last_update_time_bluetooth;

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

  char* helpMsg = "# Send: \n# 'a' for auto mode (sticks in this mode until something other is received), \n# 'z' for forward, \n# 's' for backward, \n# 'q' for turning left, \n# 'd' for turning right. \n# (WASD, but on azerty)";
  bluetooth.println(helpMsg);
  Serial.println(helpMsg);


  // a second of delay, to give time to disconnect cables etc...
  if (START_MODE == 'a' || START_MODE == 't') {
    for (int i = 0; i < 1000; i += led_speed) {
      digitalWrite(LED, HIGH);
      delay(led_speed);
      digitalWrite(LED, LOW);
      delay(led_speed);
    }
  }
  digitalWrite(LED, LOW);
  Serial.print("# Waiting for your command, now in mode ");
  Serial.println(START_MODE);
  if (BLUETOOTH_ACCEPT_ORDERS) {
    bluetooth.print("# Waiting for your command, now in mode ");
  } else {
    bluetooth.print("# Bluetooth orders disabled. Now in mode ");
  }
  bluetooth.println(START_MODE);
  last_order = START_MODE;
  send_time(1, 1);

  if (START_MODE == 't') {
    forward();
    delay(1000);
    halt();
    
  }


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
   Returns '_' if no order received
*/

char receive_orders() {
  char rd;
  if (Serial.available()) {
    return Serial.read();
  }
  if (BLUETOOTH_ACCEPT_ORDERS && bluetooth.available()) {
    rd = bluetooth.read();
    Serial.print("# Received: ");
    Serial.println(rd);
    return rd;
  }
  return '_';

}

long last_sporadic = 0;
void send_sensor_data(int left, int front, int right) {
  int send_bluetooth = 0;
  int send_serial = 0;
  long now = millis();
  int send_sporadic = 0;
  if (now - last_sporadic > SPORADIC_SENSOR_UPDATE_INTERVAL) {
    last_sporadic = now;
    send_sporadic = 1;
  }

  send_bluetooth = BLUETOOTH_SENSOR_UPDATES || (send_sporadic && BLUETOOTH_SPORADIC_SENSOR_UPDATE);
  if (send_bluetooth) {
    bluetooth.print("L");
    bluetooth.print(left);
    bluetooth.print("F");
    bluetooth.print(front);
    bluetooth.print("R");
    bluetooth.print(right);
  }

  send_serial = SERIAL_SENSOR_UPDATES || (send_sporadic && SERIAL_SPORADIC_SENSOR_UPDATE);
  if (send_serial) {
    Serial.print("  L: ");
    Serial.print(left);
    Serial.print("cm\t");
    Serial.print("  F: ");
    Serial.print(front);
    Serial.print("cm\t");
    Serial.print("  R: ");
    Serial.print(right);
    Serial.print("cm\t");
  }
  send_time(send_serial, send_bluetooth);
}


/**
   Sends the time stamp since last update
*/
void send_time(int update_serial, int update_bluetooth) {
  int now = millis();
  if (update_serial) {
    Serial.print("t");
    Serial.println(now - last_update_time_serial);
    last_update_time_serial = now;
  }
  if (update_bluetooth) {
    bluetooth.print("t");
    bluetooth.println(now - last_update_time_bluetooth);
    last_update_time_bluetooth = now;
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

void turn(int dir) {
  if (dir == LEFT) {
    turn_left();
  } else {
    turn_right();
  }
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
  // correction factor on the left wheel
  int correction = LEFT_SUM;
  if (left < 0) {
    correction = -correction;
  } else if (left == 0) {
    correction = 0;
  }

  if (old_left_speed != left || old_right_speed != right) {

    if (BLUETOOTH_MOTOR_UPDATES) {
      bluetooth.print("el");
      bluetooth.print(left);
      bluetooth.print("er");
      bluetooth.print(right);
      bluetooth.print("cor");
      bluetooth.print(correction);
    }

    if (SERIAL_MOTOR_UPDATES) {
      Serial.print("el");
      Serial.print(left);
      Serial.print("er");
      Serial.print(right);
      Serial.print("cor");
      Serial.print(correction);
    }
    send_time(SERIAL_MOTOR_UPDATES, BLUETOOTH_MOTOR_UPDATES);

    old_left_speed = left;
    old_right_speed = right;
  }

  // actually run the motors
  motors.setLeftSpeed(left + correction);
  motors.setRightSpeed(right);

}

char move_dir  = LEFT;
int last_move = 0;
long last_sporadic_auto = 0;

void auto_move(const int left, const int front, const int right) {
  int spd;
  char* mode;
  long now = millis();
  int send_sporadic = 0;

  if (now - last_sporadic_auto > SPORADIC_SENSOR_UPDATE_INTERVAL) {
    last_sporadic_auto = now;
    send_sporadic = 1;
  }



  if (front == OUT_OF_RANGE && right == OUT_OF_RANGE && left == OUT_OF_RANGE) {
    digitalWrite(LED, HIGH);
    mode = "invalid input";
  } else {
    digitalWrite(LED, LOW);
    // valid input

    if (front < 10) {

      // determine turn direction

      if (millis() - last_move > DIR_CHANGE_TIME) {
        // we can choose freely the direction to turn, as the direction holdon expired
        last_move = millis();
        Serial.println("TURNING!");
        if (right > left) {
          // there is more space on the right
          move_dir = RIGHT;
          mode = "turning left";

        } else {
          move_dir = LEFT;
          mode = "turning right";
        }

      } else {
        mode = "turning";
      }
      //actually turn

      turn(move_dir);

    } else {
      mode = "going forward";
      forward();
    }
  }

  if (SERIAL_AUTO_DEBUG || (send_sporadic && SERIAL_SPORADIC_AUTO_UPDATE)) {
    Serial.print("# auto-mode: ");
    Serial.println(mode);
    Serial.print(" last rotation:");
    Serial.println(move_dir);
    Serial.print(" last rotation moment:");
    Serial.println(last_move);

  }

  if (BLUETOOTH_AUTO_DEBUG || (send_sporadic && BLUETOOTH_SPORADIC_AUTO_UPDATE)) {
    bluetooth.print("# auto-mode: ");
    bluetooth.print(mode);
    bluetooth.print(" last rotation:");
    bluetooth.print(move_dir);
    bluetooth.print(" last rotation moment:");
    bluetooth.println(last_move);
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
  if (new_order == '_') {
    // no order received this tick
    // the default order is 'halt', only if we are in auto mode, we continue auto mode
    if (last_order == 'a') {
      new_order = 'a';
    }
  }
  last_order = new_order;

  switch (last_order) {
    case 'a': auto_move(left, front, right);  break;
    case 'z': forward();                      break;
    case 's': backward();                     break;
    case 'd': turn(LEFT);                     break;
    case 'q': turn(RIGHT);                    break;
    case 't': test_motors();                  break;
    case 'x':
    case 'S':
    case ' ': halt();                         break;
    default :                                 break;
  }

}
