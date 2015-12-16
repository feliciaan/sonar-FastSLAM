from serial import Serial
from threading import Thread
SERIAL_PORT = "/dev/tty.HC-06-DevB"

class SerialWrapper():

    def __init__(self):
        self.serial_connection = Serial(SERIAL_PORT, 9600, timeout=30)

    def write(self, var):
        if self.serial_connection:
            self.serial_connection.write(bytes(var, 'utf-8'))

    def readline(self):
        print("readlines")
        if self.serial_connection:
            line = self.serial_connection.readline()
            print(line)
            return line if line.strip() != b'' else None
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
        print("Started!\n")
        while(not self.stopped):
            message = ser.readline()
            if message:
                self.parse_message(message)

    def parse_message(self, message):
        pass

    def parse_sensor_message(self, message):
        pass

    def parse_motor_message(self, message):
        pass

inputThread = InputThread()
inputThread.start()
