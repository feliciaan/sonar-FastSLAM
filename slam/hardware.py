import re

from serial import Serial

from settings import DEBUG, SERIAL_PORT


class Hardware:
    def __init__(self):
        self.serial = None
        if DEBUG:
            self.file = 'nieuwedata1.txt'
        else:
            self.serial = Serial(SERIAL_PORT, 9600, timeout=30)

    def updates(self):
        data_iterator = open(self.file) if DEBUG else self.serial_data()
        for line in data_iterator:
            yield parse(line.strip())

    def serial_data(self):
        while True:
            message = self.readline()
            if message:
                yield message

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


class MotionUpdate:
    def __init__(self, line):
        match = re.match('el(-?\d+)er(-?\d+)cor(-?\d+)t(\d+)', line)
        self.left = int(match.group(1))
        self.right = int(match.group(2))
        self.correction = int(match.group(3))
        self.timedelta = int(match.group(4))


def parse(self, line):
    if line.startswith('#'):
        return None
    elif line.startswith('L'):
        return SensorUpdate(line)
    else:
        return MotionUpdate(line)
