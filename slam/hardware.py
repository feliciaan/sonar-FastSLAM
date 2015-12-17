import re


class Hardware:
    def updates(self):
        for line in open('test6.txt'):
            yield parse(line.strip())


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
