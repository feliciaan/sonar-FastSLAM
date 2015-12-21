import math
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
        if measured_dist is None:
            measured_dist = 130
            measurement = False

        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)

        cone = map_.get_cone(sensor_pose, CONE_ANGLE, measured_dist)
        for (cell, d) in cone:
            relative_dist   = d / measured_dist
            if relative_dist < 0.8:
                cell.add_log_odds(_log_odds(0.3))
            elif measurement:
                cell.add_log_odds(_log_odds(0.7))


def _measurement_per_angle(measurements):
    return [
        (math.pi / 2, measurements.left),
        (0, measurements.front),
        (-math.pi / 2, measurements.right),
    ]


def _log_odds(p):
    return math.log(p / (1 - p))
