import random
import math
import numpy
from pose import Pose

STD_DEV = 2
THETA_STD_DEV = .1
WHEEL_DISTANCE_IN_CM = 8.4


# FACTOR    voltage = 4.3 volt
#           90 pixels = 90 cemeters (gridworld::BLOCK = 5)
FACTOR = 0.00014
WHEEL_RADIUS = 0.015  # m

# GAUSSIAN NOISE
GAUSSIAN_NOISE = True
# local rotation
ANGLE_GAUSS_TURNING = 0.1
# STRAIGHT line
STRAIGHT_ANGLE = 0.02
STRAIGHT_DIST = 0.1


# radians during 1 angle turn depending on surface ...
# 30 degrees for voltage = 4.3 volt
RADIANS_DURING_1_turn = 0.314  # 0.54  # 40 degrees



def calculate_pose(old_pose, motion, timedelta, map):
    """Calculates a possible new position, with added gaussian noise."""

    distance_left = motion.left * timedelta * FACTOR
    distance_right = motion.right * timedelta * FACTOR

    if distance_left == distance_right:
        dx = distance_left * math.cos(old_pose.theta)
        dy = distance_left * math.sin(old_pose.theta)
        dtheta = 0
    elif distance_left == -distance_right:
        dx, dy = 0, 0
        #dtheta = #timedelta * (math.pi / 4) / MS_PER_45_DEGREES
        dtheta = RADIANS_DURING_1_turn
        if distance_left > 0:
            dtheta *= -1
            # dtheta=distance_left/(WHEEL_DISTANCE_IN_CM/2) #left turn results in positive dtheta, uses formula length arc


    if dx == 0.0 and dtheta == 0.0:
        return Pose(old_pose.x, old_pose.y, old_pose.theta)

    if GAUSSIAN_NOISE:

        if dx == 0.0 and dy == 0.0:
            return sample_rotation(old_pose, dtheta)

        elif dtheta == 0.0:
            return sample_forward_move(old_pose, dx, dy, map)
        else:
            print('dx, dy and dtheta are not zero ??')
            exit()
    else:
        return Pose(old_pose.x + dx, old_pose.y + dy, old_pose.theta + dtheta)

def sample_rotation(old_pose, dtheta):

    new_x_with_noise = old_pose.x
    new_y_with_noise = old_pose.y
    new_theta_with_noise = random.gauss(old_pose.theta + dtheta, ANGLE_GAUSS_TURNING)
    return Pose(new_x_with_noise, new_y_with_noise, new_theta_with_noise)

def sample_forward_move(old_pose, dx, dy, map):
    sampled_poses=[]
    sample_weight=[]
    # calculate distance to new point
    dist = math.sqrt(dx**2 + dy**2)
    # angle to the point on circle  == old_pose.theta
    angle = math.atan2(dy,dx)
    # print (angle)
    # old_pose.theta
    # print(old_pose.theta)

    NUM_SAMPLES = 8
    # generate 4 possibilities and select the one with the lowest occupancy correspondence
    for i in range(0,NUM_SAMPLES):
        sample_dist = random.gauss(dist, STRAIGHT_DIST)
        sample_angle = random.gauss(angle, STRAIGHT_ANGLE)

        sample_dy = sample_dist * math.sin(sample_angle)
        sample_dx = sample_dist * math.cos(sample_angle)

        new_x_with_noise = old_pose.x + sample_dx
        new_y_with_noise = old_pose.y + sample_dy
        new_theta_with_noise = sample_angle
        sample = Pose(new_x_with_noise, new_y_with_noise, new_theta_with_noise)
        # print (sample)
        sampled_poses.append(sample)

        # take into account the map when selecting a new pose
        weight = calc_weight_sample(map, sample)
        sample_weight.append(weight)

    # search index highest weight
    # print(sample_weight)
    index = numpy.argmin(sample_weight)
    if index != 0:
        print ('index : ', index)
    return sampled_poses[index]



def calc_weight_sample(map, sample):

    grid_index = map.cartesian2grid(sample.x, sample.y)
    weight = 0
    # look in a range around the sampled pose
    RANGE = 5
    for i in range(-RANGE, RANGE + 1, 1):
        for j in range(-RANGE, RANGE + 1, 1):
            pos = (grid_index[0] + i, grid_index[1] + j)
            weight += calc_weight_pose(map, pos)

    return weight


def calc_weight_pose(map, pos):

    WEIGHT_UNEXPLORED = 1
    # print (pos)
    if (not map.in_grid(pos)):
        # sample not on map
        return WEIGHT_UNEXPLORED

    cell = map.get_cell(pos[0], pos[1])
    if proc_value_cell(cell) == 0.5:
        # map point is unexplored
        return WEIGHT_UNEXPLORED

    # map point is explored
    prob_cell_occupied = proc_value_cell(cell)
    assert prob_cell_occupied >= 0, 'prob should be bigger than 0'
    return prob_cell_occupied


"""
   value cell calculated as a value between 0 and 1
"""

def proc_value_cell(cell):
    proc_value = 1 - 1 / (1 + math.exp(min(500, cell)))  # procentual value
    return proc_value







# TODO change error parameters to improve result (if using sample motion model)
# error parameters
ERROR1 = 1  # translational error
ERROR2 = 1  # translational error
ERROR3 = 0.0001  # angular error
ERROR4 = 0.001  # angular error

# new_pose = Pose(old_pose.x+dx, old_pose.y+dy, old_pose.theta+dtheta)
# return sample_motion_model(Pose(0,0,0), Pose(0+dx,0+dy,0+dtheta), old_pose)


# # TODO fix: doesn't work as it ought to yet
# " implementing algorithm sample motion model odometry  Thrun p136"
#
#
# def sample_motion_model(old_pose_local, new_pose_local, old_pose_global):
#     delta_rot1 = math.atan2(new_pose_local.y - old_pose_local.y,
#                             new_pose_local.x - old_pose_local.x) - old_pose_local.theta
#     delta_trans = math.sqrt((old_pose_local.x - new_pose_local.x) ** 2 + (old_pose_local.y - new_pose_local.y) ** 2)
#     delta_rot2 = new_pose_local.theta - old_pose_local.theta - delta_rot1
#
#     delta_rot1_sample = delta_rot1 - sample(ERROR1 * delta_rot1 ** 2 + ERROR2 * delta_trans ** 2)
#     delta_trans_sample = delta_trans - sample(
#         ERROR3 * delta_trans ** 2 + ERROR4 * delta_rot1 ** 2 + ERROR4 * delta_rot2 ** 2)
#     delta_rot2_sample = delta_rot2 - sample(ERROR1 * delta_rot2 ** 2 + ERROR2 * delta_trans ** 2)
#
#     x_new = old_pose_global.x + delta_trans_sample * math.cos(old_pose_global.theta + delta_rot1_sample) if (
#     new_pose_local.x != 0) else (old_pose_global.x + new_pose_local.x)
#     y_new = old_pose_global.y + delta_trans_sample * math.sin(old_pose_global.theta + delta_rot1_sample) if (
#     new_pose_local.y != 0) else (old_pose_global.y + new_pose_local.y)
#     theta_new = old_pose_global.theta + delta_rot1_sample + delta_rot2_sample if (new_pose_local.theta != 0) else (
#     old_pose_global.theta + new_pose_local.theta)
#
#     return Pose(x_new, y_new, theta_new)
#
#
# def sample(b_squared):
#     return sample_normal_distribution(b_squared)
#
#
# def sample_normal_distribution(b_squared):
#     sum = 0
#     b = math.sqrt(b_squared)
#     for i in range(0, 12):
#         sum += random.uniform(-1 * b, b)
#     return 1 / 2 * sum
