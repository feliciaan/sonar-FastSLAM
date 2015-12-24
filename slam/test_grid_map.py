"""
Walks through the grid map, in a very naive way
"""
import time
from grid_map import OccupancyGridMap
from hardware import *
from pose import Pose
from motion_model import calculate_pose
from state import State
from settings import DEBUG
import math

INF = 500

hw = Hardware("../test/testdata-film-feli01.txt")
state = State(n_particles=100, cellsize=5, blocksize=100)

old_pose = Pose(0, 0, 0)

i = 0
ogm = None
sumdeltas = 0
for update in hw.updates():
    start_time = time.time()
    state.update(update)
    particle = state.particles[0]
    ogm = particle.map
    pose = particle.pose
    # ogm.get_cell(old_pose.x, old_pose.y).hasRobot = None

    cell = ogm.get_cell(pose.x, pose.y)
    # cell.hasRobot = pose.dir_str() #TODO: save robot path
    cell = -INF
    old_pose = pose
    i += 1
    #if i % 25 == 0:
    #    print(ogm)
    #    print(ogm.distance_to_closest_object_in_cone(pose, 0.872664626, 130))
    stop_time = time.time()
    timedelta = update.timedelta - (stop_time - start_time) * 1000
    sumdeltas += timedelta
    if timedelta < 0:
        print("Slower than updates: %f, current delay %f" % (timedelta, sumdeltas))
    else:
        print("Faster than updates: %f, current delay %f" % (timedelta, sumdeltas))
print(sumdeltas)
print(ogm)
