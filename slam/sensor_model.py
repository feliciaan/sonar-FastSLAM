import math
import numpy
from pose import Pose
from tuple_utils import tsub
from grid_map import procentual_grid

MAX_RANGE = 150  # In cm
CONE_ANGLE = 0.872664626  # In radians
PROBABILITY_FREE = 0.001
RECOGNITION_SENSITIVITY = 10  # In cm


def calc_weight(measurements, pose, map_):
    probability = 1
    # return probability

    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)

        # TODO: what if no expected distance is known? Fixed -> weight

        """likelihoods fields range finder, p172"""
        if measured_dist is not None and measured_dist < MAX_RANGE:  # discard max range readings

            # coordinates of endpoint measured distance
            x_co = sensor_pose.x + measured_dist * math.cos(sensor_pose.theta)
            y_co = sensor_pose.y + measured_dist * math.sin(sensor_pose.theta)

            nearest_object = find_nearest_neighbor(map_, (x_co, y_co))
            # when sensor measurement falls into unknown category, prob is assumed constant p173
            if nearest_object == "unknown":
                # measurement => there is something
                # map => I don't know it ...
                # OLD --> probability *= 1 / MAX_RANGE
                # NEW --> don't touch the weight of the particle
                None

            # find nearest neighbour that is occupied
            elif nearest_object is not None:
                # calculate Euclidean distance between measured coord and closest occupied coord
                sub = tsub((x_co, y_co), nearest_object)
                distance = math.hypot(sub[0], sub[1])
                prob = _prob_of_distances(distance, 0.0)
                probability *= prob

        else:
            # TODO: if there is no measurement --> probability stays 1 ?
            # if sensor got OUT of range --> particle gets higher chance ??
            None

    return probability


"""
   value cell calculated as a value between 0 and 1
"""


def proc_value_cell(cell):
    proc_value = 1 - 1 / (1 + math.exp(min(500, cell)))  # procentual value
    return proc_value


"""
finds nearest occupied cell for cell with given position
    if the position is outside the grid, the cell is unknown
    if the cell is inside the grid but has value 0.5, the cell is unknown
    if the cell has value 1, the cell itself is occupied, return cell
        otherwise look for nearest occupied neighbour--> use grid coord (row,column) and circle around cell with increasing distance
        occupied cell found if value ==1 

"""


def find_nearest_neighbor(map, position):
    NN_THRESHOLD = 0.9
    grid_index = map.cartesian2grid(position[0], position[1])
    if (not map.in_grid(grid_index)):
        return "unknown"

    cell = map.get_cell(position[0], position[1])
    if proc_value_cell(cell) == 0.5:
        return "unknown"

    # measured cell is occupied
    if proc_value_cell(cell) > NN_THRESHOLD:
        return position
    else:

        '''
        This looks for closests neighboring cell of endpoint cone
        --> It looks in a circle around this point
        OPTIMIZATION:
            Should be better to look in an oval kind of shape
        '''
        distance = 1
        # check in radius around current position, using (row,column) positions in grid
        # if counter is 0, no occupied positions inside the grid have been found, return None
        counter = -1
        while counter != 0:
            counter = 0
            for i in range(0, distance + 1, 1):
                for a in (-1, 1):
                    for b in (-1, 1):
                        pos = (grid_index[0] + a * distance, grid_index[1] + b * i)
                        if (map.in_grid(pos)):
                            if proc_value_cell(map.grid[pos[0], pos[1]]) > NN_THRESHOLD:
                                counter += 1
                                return map.grid2cartesian(pos[0], pos[1])

                        pos = (grid_index[0] + a * i, grid_index[1] + b * distance)
                        if (map.in_grid(pos)):
                            if proc_value_cell(map.grid[pos[0], pos[1]]) > NN_THRESHOLD:
                                counter += 1
                                return map.grid2cartesian(pos[0], pos[1])
                                # print('counter: ', counter)
            distance += 1
        return None


def distance_to_closest_object_in_cone(map, pose, cone_width_angle, max_radius):
    # NOT used yet...
    """
        Raytraces until a first object is found. Does not search further then max_radius.
        Keep max_radius quite small (e.g. 130cm or 200cm), as it will get slow otherwise.

        Returns the pareto-front of (distance, log_odds). None-values are ignored
        """
    # print('max_radius', max_radius)

    coors, distances = map.get_cone(pose, cone_width_angle, max_radius)

    # map.grid = procentual_grid(map.grid)

    # def snd(tupl):
    #     (x, y) = tupl
    #     return y

    # cells = list(cells)
    # cells.sort(key=snd)

    cells = zip(coors, distances)
    cells = sorted(cells, key = lambda t: t[1])
    # print (cells)
    # print('hallo')
    # [ print(x) for x  in cells ]
    # exit()

    OCC_THRESHOLD = 0.55
    NUM_HITS_THRESHOLD = 20
    # looks in the cone for NUM_HITS_THRESHOLD locations with occupancy
    # probability higher than OCC_THRESHOLD

    occupied = False
    num_hits = 0

    for (cell, d) in cells:
        cell = map.get_cell(*cell)
        value = proc_value_cell(cell)
        # print('value : ', value)
        if value > OCC_THRESHOLD:
            # probs.append(value)
            num_hits += 1

    # print (len(cells))

    print('num_hits : ', num_hits)
    if num_hits > NUM_HITS_THRESHOLD:
        occupied = True

    return occupied


def _prob_of_distances(measured, expected):
    return _normal_distribution(measured, expected, RECOGNITION_SENSITIVITY)


def _normal_distribution(x, mean, stddev):
    den = (math.sqrt(2 * math.pi) * stddev)
    return 1 / den * math.exp((-1 * ((x - mean) ** 2)) / (2 * (stddev ** 2)))


def update_map(measurements, pose, map_):
    # set the space around the robot FREE
    robot_pose = Pose(pose.x, pose.y, pose.theta)
    grid_index = map_.cartesian2grid(robot_pose.x, robot_pose.y)

    robot_coords = []
    PATH_WIDTH = 4
    for i in range(-PATH_WIDTH, PATH_WIDTH + 1, 1):
        for j in range(-PATH_WIDTH, PATH_WIDTH + 1, 1):
            pos = (grid_index[0] + i, grid_index[1] + j)
            if (map_.in_grid(pos)):
                robot_coords.append(pos)

    for coords in robot_coords:
        map_.grid[coords[0], coords[1]] += _log_odds(PROBABILITY_FREE)

    for sensor_angle, measured_dist in _measurement_per_angle(measurements):

        measurement = True
        if measured_dist is None or measured_dist >= MAX_RANGE:
            measured_dist = MAX_RANGE
            measurement = False

            # measured_dist > MAX_RANGE --> short reading or indeed nothing


        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)

        cell_coordinates, distances = map_.get_cone(sensor_pose, CONE_ANGLE,
                                                    measured_dist)
        # measured distance on old map --> cell_coordinates that should be updated


        if measurement:

            CUTOFF_FACTOR = 0.4

            cutoff = measured_dist * CUTOFF_FACTOR
            empty_coords = cell_coordinates[distances < cutoff]
            non_empty_coords = cell_coordinates[distances > cutoff]

            map_.grid[empty_coords[:, 0], empty_coords[:, 1]] += _log_odds(PROBABILITY_FREE)

            non_empty_distances = distances[distances > cutoff]
            max_dist = max(non_empty_distances)

            UNCERTAINTY_GRADIENT = 0.1  # below 0.5 please ...

            non_empty_log_odds = []
            for i, entry in enumerate(non_empty_distances):
                factor = UNCERTAINTY_GRADIENT * (non_empty_distances[i] / max_dist)
                non_empty_log_odds.append(_log_odds(.5 + factor))
            map_.grid[non_empty_coords[:, 0], non_empty_coords[:, 1]] += non_empty_log_odds

            # print(len(non_empty_coords))
            # print(max(distances[distances>cutoff]))
            # print(non_empty_log_odds)
            # print(_log_odds(PROBABILITY_FREE))
            # exit()

            # map_.grid[cell_coordinates[:, 0], cell_coordinates[:, 1]] += _log_odds(PROBABILITY_FREE)

        else:
            # max reading
            # look if there is an obstacle on the map
            # calculate
            MAX_RADIUS =70
            # MAX_RANGE = 150
            print('Measured_dist : ', measured_dist)
            print('sensor_angle : ', sensor_angle)
            cell_coordinates = cell_coordinates[distances < MAX_RADIUS]
            occupied = distance_to_closest_object_in_cone(map_, sensor_pose, CONE_ANGLE, MAX_RADIUS)
            # print(found)
            #
            #
            if occupied:
                SHORT_READING_PROB = 0.7
                map_.grid[cell_coordinates[:, 0], cell_coordinates[:, 1]] += _log_odds(SHORT_READING_PROB)
            else:
                map_.grid[cell_coordinates[:, 0], cell_coordinates[:, 1]] += _log_odds(PROBABILITY_FREE)

            # if measurement and len(non_empty_coords) > 0:
            #    non_empty_log_odds = _log_odds(.5 + (.01 / (len(non_empty_coords) + 1)))
            #    map_.grid[non_empty_coords[:, 0], non_empty_coords[:, 1]] += non_empty_log_odds


def _measurement_per_angle(measurements):
    return [
        (math.pi / 2, measurements.left),
        (0, measurements.front),
        (-math.pi / 2, measurements.right),
    ]


def _log_odds(p):
    return math.log(p / (1 - p))
