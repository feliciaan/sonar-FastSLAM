import math

class Pose:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def __str__(self):

        degrees = math.degrees(self.theta) % 360
        if degrees > 180:
            degrees -= 360

        return "Pose: x:"+str(int(self.x))+"cm, y:"+\
               str(int(self.y))+",cm θ :"+str(self.theta)+" θ:"+str(degrees)

    def dir_str(self):
        chars   = "↑↗→↘↓↙←↖"
        # as a float, 0..1, where 0 and 1 are 360°, 0.5 = 180°
        theta   = (self.theta + 2*math.pi) / (2*math.pi)
        theta   = ((theta + 1/16) * 8) % 8
        return chars[int(theta)]
