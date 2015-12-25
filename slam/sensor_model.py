import math
import numpy as np
from pose import Pose

CONE_ANGLE = 0.872664626  # In radians
PROBABILITY_FREE = 0.0001
RECOGNITION_SENSITIVITY = 5


def calc_weight(measurements, pose, map_):
    probability = 1
    return probability # TODO remove
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        if measured_dist is None:
            measured_dist = 130
        if measured_dist > 200:
            measured_dist = 200
        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)
        # TODO: what if no expected distance is known? Fixed -> weight
        expected_distance = \
            map_.distance_to_closest_object_in_cone(sensor_pose, CONE_ANGLE)
        probability *= _prob_of_distances(measured_dist, expected_distance)

    return probability


def _prob_of_distances(measured, expected):
    return _normal_distribution(measured, expected, RECOGNITION_SENSITIVITY)


def _normal_distribution(x, mean, stddev):
    denominator = (math.sqrt(2 * math.pi) *
                   stddev *
                   math.exp(((x - mean) ** 2) / (2 * (stddev ** 2))))
    return 1 / denominator


def update_map(measurements, pose, map_):
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        measurement = True
        if measured_dist is None or measured_dist > 130:
            measured_dist = 130
            measurement = False

        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)

        indices, dist = map_.get_cone(sensor_pose, CONE_ANGLE, measured_dist)
        if indices.size == 0:
            continue
        map_.check_indices_in_bounds(indices)

        # modify to grid indices
        indices = np.rint(indices / map_.cellsize - map_.minrange).astype(np.int)

        cutoff = measured_dist * 0.8
        empty_indices = indices[dist < cutoff]

        map_.grid[empty_indices[:, 0], empty_indices[:, 1]] += -0.8472978603872036  # _log_odds(0.3)
        if measurement:
            non_empty_indices = indices[dist >= cutoff]
            map_.grid[non_empty_indices[:, 0], non_empty_indices[:, 1]] += 0.8472978603872034  # _log_odds(0.7)


def _measurement_per_angle(measurements):
    return [
        (math.pi / 2, measurements.left),
        (0, measurements.front),
        (-math.pi / 2, measurements.right),
    ]


def _log_odds(p):
    return math.log(p / (1 - p))
