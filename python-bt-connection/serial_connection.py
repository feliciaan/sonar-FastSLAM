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
                yield message


inputThread = InputThread()
inputThread.start()
