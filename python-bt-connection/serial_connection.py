from serial import Serial
from threading import Thread
SERIAL_PORT = "/dev/tty.HC-06-DevB"

SENSOR = 'sensor'
MOTOR = 'motor'


class SerialWrapper():

    def __init__(self):
        self.serial_connection = Serial(SERIAL_PORT, 9600, timeout=30)

    def write(self, var):
        if self.serial_connection:
            self.serial_connection.write(bytes(var, 'utf-8'))

    def readline(self):
        print('readline')
        if self.serial_connection:
            line = self.serial_connection.readline()
            return line.decode('utf-8').strip() if line.strip() != b'' else None
        return None

    def close(self):
        if self.serial_connection:
            self.serial_connection.close()

ser = SerialWrapper()
class InputThread(Thread):

    def __init__(self):
        super(InputThread, self).__init__()
        self.stopped = False

    def run(self):
        while(not self.stopped):
            message = ser.readline()
            if message:
                print(self.parse_message(message))

    def parse_message(self, message):
        if message[0] == 'L':
            return self.parse_sensor_message(message)
        elif message[0] == 'e':
            return self.parse_motor_message(message)

    def parse_sensor_message(self, message):
        before, after = message.split('F')
        left_sensor = before.split('L')[-1]
        front_sensor, after = after.split('R')
        right_sensor, timestamp = after.split('t')

        return (SENSOR, int(left_sensor), int(front_sensor), int(right_sensor), int(timestamp))

    def parse_motor_message(self, message):
        message = message[2:]
        left_motor, other = message.split('er')
        right_motor, other = other.split('cor')
        correction, timestamp = other.split('t')

        return (MOTOR, int(left_motor), int(right_motor), int(correction), int(timestamp))

inputThread = InputThread()
inputThread.start()
