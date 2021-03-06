import math


class Pose:
    CHARS = "→↗↑↖←↙↓↘"

    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def __str__(self):
        degrees = math.degrees(self.theta) % 360
        if degrees > 180:
            degrees -= 360

        template = "Pose: x:{}cm, y:{}cm, \u03B8:{}, rad={}°"
        return template.format(self.x, self.y, self.theta, degrees)

    def dir_str(self):
        # as a float, 0..1, where 0 and 1 are 360°, 0.5 = 180°
        #print("theta")
        #print(self.theta)
        theta = (self.theta + 2*math.pi) / (2*math.pi)
        theta = ((theta + 1/16) * 8) % 8
        #print(theta)
        return self.CHARS[int(theta)]
