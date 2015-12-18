import math
from state import Pose

CONE_ANGLE = 0.872664626  # In radians
PROBABILITY_FREE = 0.0001


def calc_weight(measurements, pose, map_):
    probability = 1

    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        if measured_dist is None:
            continue
        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)
        expected_distance = \
            map_.distance_to_closest_object_in_cone(sensor_pose, CONE_ANGLE)
        probability *= _prob_of_distances(measured_dist, expected_distance)

    return probability


def _prob_of_distances(measured, expected):
    return 1 / abs(measured - expected)


def update_map(measurements, pose, map_):
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        if measured_dist is None:
            continue

        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)

        cone = map_.get_cone(sensor_pose, CONE_ANGLE, measured_dist)

        for cell in cone.edge:
            cell.occupied += _log_odds(.5 + (.5 / len(cone.edge)))

        for cell in cone.inside:
            cell.occupied += _log_odds(PROBABILITY_FREE)


def _measurement_per_angle(measurements):
    return [
        (math.pi / 2, measurements.left),
        (0, measurements.front),
        (-math.pi / 2, measurements.right),
    ]


def _log_odds(p):
    return math.log(p / (1 - p))
