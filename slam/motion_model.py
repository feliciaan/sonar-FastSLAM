import random
import math
from pose import Pose

STD_DEV = .2
THETA_STD_DEV = .05
WHEEL_DISTANCE_IN_CM = 8.4
FACTOR = 1 / 600  # Empirically found

"""
Calculates a possible new position, with added gaussian noise.
"""
def calculate_pose(old_pose, motion, timedelta):
    distance_left = motion.left * timedelta * FACTOR
    distance_right = motion.right * timedelta * FACTOR

    if distance_left == distance_right:
        dx = distance_left * math.cos(old_pose.theta)
        dy = distance_left * math.sin(old_pose.theta)
        dtheta = 0
    elif distance_left == -distance_right:
        dx, dy = 0, 0
        dtheta = timedelta * math.pi / (2 * 250)
        if distance_left > distance_right:
            dtheta *= -1
    else:
        turning_angle = (distance_left - distance_right) / WHEEL_DISTANCE_IN_CM
        polar_length = (distance_left + distance_right) / (2 * turning_angle)

        dx = polar_length * (math.cos(turning_angle) - 1)
        dy = polar_length * math.sin(turning_angle)
        dtheta = turning_angle

    dx_with_noise = random.gauss(dx, STD_DEV) if dx != 0 else 0
    dy_with_noise = random.gauss(dy, STD_DEV) if dy != 0 else 0
    dtheta_with_noise = (random.gauss(dtheta, THETA_STD_DEV)
                         if dtheta != 0 else 0)

    return Pose(old_pose.x + dx_with_noise,
                old_pose.y + dy_with_noise,
                old_pose.theta + dtheta_with_noise)
