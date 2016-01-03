import math


class Pose:
    CHARS = "→↙↓↘↗←↑↖"

    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def __str__(self):
        degrees = math.degrees(self.theta) % 360
        if degrees > 180:
            degrees -= 360

        template = "Pose: x:{.0f}cm, y:{.0f}cm, θ:{.2f}rad={}°"
        return template.format(self.x, self.y, self.theta, degrees)

    def dir_str(self):
        # as a float, 0..1, where 0 and 1 are 360°, 0.5 = 180°
        theta = (self.theta + 2*math.pi) / (2*math.pi)
        theta = ((theta + 1/16) * 8) % 8
        return self.CHARS[int(theta)]
