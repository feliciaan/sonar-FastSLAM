import re


"""
Use updates(filelocation) to get a neat list of updates.
"""

class SensorUpdate:
    def __init__(self, line = None):
        match = re.match('L(\d+)F(\d+)R(\d+)t(\d+)', line)
        assert match is not None, "Invalid input for sensor update: "+line
        self.left = int(match.group(1))
        self.front = int(match.group(2))
        self.right = int(match.group(3))
        self.timedelta = int(match.group(4))

    def __str__(self):
        return "SensorUpdate L: "+str(self.left)+"cm, R: "+str(self.right)+"cm, F:"+str(self.front)+" time: "+str(self.timedelta)+"ms"


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
        return "MotionUpdate L: "+str(self.left)+", R: "+str(self.right)+", time: "+str(self.timedelta)+"ms"


def updates(locatie):
    for line in open(locatie):
        yield _parse(line.strip())


def _parse(line):
    if line.startswith('#'):
        return None
    elif line.startswith('L'):
        return SensorUpdate(line)
    else:
        return MotionUpdate(line)
