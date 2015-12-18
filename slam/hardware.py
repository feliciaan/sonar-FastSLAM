import re

from serial import Serial
from serial.serialutil import SerialException

from settings import DEBUG, SERIAL_PORT


class Hardware:
    def __init__(self):
        self.serial = None
        print("DEBUG MODE: %d" % DEBUG)
        if DEBUG:
            self.file = '../test/nieuwedata1.txt'
        else:
            try:
                self.serial = Serial(SERIAL_PORT, 9600, timeout=1)
            except SerialException:
                print("Serial connection could not be opened!")

    def updates(self):
        data_iterator = open(self.file) if DEBUG else self.serial_data()
        for line in data_iterator:
            line = line.strip()
            if line:
                yield parse(line)

    def write(self, action):
        if self.serial:
            self.serial.write(bytes(var, 'utf-8'))

    def serial_data(self):
        while True:
            message = self.serial.readline().decode('utf-8').strip()
            message = message if message != '' else None
            if message:
                yield message


class SensorUpdate:
    def __init__(self, line):
        match = re.match('L(\d+)F(\d+)R(\d+)t(\d+)', line)
        self.left = int(match.group(1))
        self.front = int(match.group(2))
        self.right = int(match.group(3))
        self.timedelta = int(match.group(4))

    def __str__(self):
        return "SensorUpdate(Left: %d\tFront: %d\tRight: %d\tTimedelta: %d)" \
            % (self.left, self.front, self.right, self.timedelta)


class MotionUpdate:
    def __init__(self, line):
        match = re.match('el(-?\d+)er(-?\d+)cor(-?\d+)t(\d+)', line)
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
