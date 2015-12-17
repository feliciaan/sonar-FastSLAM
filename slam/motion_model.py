import random
import math
from state import Pose
import grid_map

STD_DEV = .2
THETA_STD_DEV = .05
WHEEL_DISTANCE_IN_CM = 8.4
WHEEL_DISTANCE = WHEEL_DISTANCE_IN_CM / grid_map.CELL_SIZE
FACTOR = 1 / 600  # Empirically found


def calculate_pose(old_pose, motion, timedelta):
    distance_left = motion.left * timedelta * FACTOR / grid_map.CELL_SIZE
    distance_right = motion.right * timedelta * FACTOR / grid_map.CELL_SIZE

    if distance_left == distance_right:
        dx = distance_left * math.cos(old_pose.theta)
        dy = distance_left * math.sin(old_pose.theta)
        dtheta = 0
        print("first case", dx, dy, dtheta)
    elif distance_left == -distance_right:
        dx, dy = 0, 0
        dtheta = timedelta * math.pi / (2 * 250)
        if distance_left > distance_right:
            dtheta *= -1
    else:
        turning_angle = (distance_left - distance_right) / WHEEL_DISTANCE
        polar_length = (distance_left + distance_right) / (2 * turning_angle)
        print('left', distance_left)
        print('right', distance_right)
        print('wheels', WHEEL_DISTANCE)
        print('angle', turning_angle)
        print('polar', polar_length)

        dx = polar_length * (math.cos(turning_angle) - 1)
        dy = polar_length * math.sin(turning_angle)
        dtheta = turning_angle
        print("second case", dx, dy, dtheta)

    dx_with_noise = random.gauss(dx, STD_DEV) if dx != 0 else 0
    dy_with_noise = random.gauss(dy, STD_DEV) if dy != 0 else 0
    dtheta_with_noise = (random.gauss(dtheta, THETA_STD_DEV)
                         if dtheta != 0 else 0)

    return Pose(old_pose.x + dx_with_noise,
                old_pose.y + dy_with_noise,
                old_pose.theta + dtheta_with_noise)
