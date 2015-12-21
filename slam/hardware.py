import re

import threading
import time
SERIAL_AVAILABLE = True
try:
        from serial import Serial
        from serial.serialutil import SerialException
except ImportError:
        print("Importing serial failed! Only file imports will be supported")
        SERIAL_AVAILABLE = False

class Hardware:
    def __init__(self, testfile=None, serial_port=None):
        self.serial = None
        self.t = None
        self.read_input = True
        assert (testfile is None) != (serial_port is None), "You should either pass a 'testfile' or a 'serial_port' to initialize"
        self.file = testfile
        if SERIAL_AVAILABLE and serial_port is not None:
            try:
                self.serial = Serial(serial_port, 9600, timeout=1)
            except SerialException:
                print("Serial connection could not be opened! Please, check the code to see why :p")

        self.t = threading.Thread(target=self.send_messages)
        self.t.start()



    def updates(self):
        data_iterator = self.serial_data() if SERIAL_AVAILABLE and self.serial else open(self.file)
        for line in data_iterator:
            line = line.strip()
            if line:
                yield parse(line)
            time.sleep(1)
        if self.t:
            self.read_input = False

    def write(self, action):
        if self.serial:
            self.serial.write(bytes(action, 'utf-8'))

    def serial_data(self):
        while True:
            message = self.serial.readline().decode('utf-8').strip()
            message = message if message != '' else None
            if message:
                yield message

    def send_messages(self):
        while self.read_input:
            i = input()
            print(i)

class SensorUpdate:
    def __init__(self, line = None):
        if line is None:
            line = "L0F0R0t0"
        match = re.match('L(\d+)F(\d+)R(\d+)t(\d+)', line)
        assert match is not None, "Invalid input for sensor update: "+line

        def out_of_range(s):
            i = int(s)
            if i == 9999:
                return None
            return i

        self.left = out_of_range(match.group(1))
        self.front = out_of_range(match.group(2))
        self.right = out_of_range(match.group(3))
        self.timedelta = out_of_range(match.group(4))

    def __str__(self):
        def n(i):
            if i is None:
                return 9999
            return i
        return "SensorUpdate(Left: %dcm\tFront: %dcm\tRight: %dcm\tTimedelta: %dms)" \
            % (n(self.left), n(self.front), n(self.right), n(self.timedelta))


class MotionUpdate:
    def __init__(self, line = None):
        if line is None:
            line = "el0er0cor0t0"
        match = re.match('el(-?\d+)er(-?\d+)cor(-?\d+)t(\d+)', line)
        assert match is not None, "Invalid input for motion update: "+line
        self.left = int(match.group(1))
        self.right = int(match.group(2))
        self.correction = int(match.group(3))
        self.timedelta = int(match.group(4))

    def __str__(self):
        return "MotionUpdate(Left: %d\tRight: %d\tTimedelta: %d)" \
            % (self.left, self.right, self.timedelta)

def parse(line):
    if line.startswith('#'):
        return None
    elif line.startswith('L'):
        return SensorUpdate(line)
    elif line.startswith('el'):
        return MotionUpdate(line)
    else:
        return None
