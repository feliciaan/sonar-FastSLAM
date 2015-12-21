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
import sys

import readchar

CONVERT_CHARS = {'\x1b\x5b\x41':'z', '\x1b\x5b\x42':'s', '\x1b\x5b\x44':'q','\x1b\x5b\x43':'d'}

class Hardware:
    def __init__(self, testfile=None, serial_port=None, output_file=None):
        self.serial = None
        self.t = None
        self.read_input = True
        assert (testfile is None) != (serial_port is None), "You should either pass a 'testfile' or a 'serial_port' to initialize"
        self.file = testfile
        self.output_file = output_file
        if SERIAL_AVAILABLE and serial_port is not None:
            try:
                self.serial = Serial(serial_port, 9600, timeout=1)
                 # Different thread for manual control
                self.t = threading.Thread(target=self.send_messages)
                self.t.start()
            except SerialException:
                print("Serial connection could not be opened! Please, check the code to see why :p")

    def updates(self):
        data_iterator = self.serial_data() if SERIAL_AVAILABLE and self.serial else open(self.file)
        for line in data_iterator:
            line = line.strip()
            if line:
                yield parse(line)
        if self.t:
            self.read_input = False

    def write(self, action):
        if self.serial:
            self.serial.write(bytes(action, 'utf-8'))
        print("Sending to robot:", action)

    def serial_data(self):
        output = self.output_file if self.output_file else '/dev/null'
        print(output)
        with open(output, mode='a', newline='\n') as f:
            while True:
                message = self.serial.readline().decode('utf-8').strip()
                f.write(message)
                print(message)
                message = message if message != '' else None
                if message:
                    yield message

    def send_messages(self):
        print("Reading input:")
        while self.read_input:
            key = readchar.readkey()
            if key in ['\x03', '\x04']: # if control-c stop
                print("Retuning control to the program")
                self.read_input = False
                break

            if len(key) == 1:
                self.write(key)
            else:
                # convert to other thing if necessary
                new_c = CONVERT_CHARS.get(key)
                if new_c:
                    self.write(new_c)



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
