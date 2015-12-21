"""
Walks through the grid map, in a very naive way
"""
import time
from grid_map import OccupancyGridMap
from cell import Cell
from hardware import *
from pose import Pose
from motion_model import calculate_pose
from state import State
import math

INF = 500

hw  = Hardware(serial_port='/dev/tty.HC-06-DevB', output_file='testdata.txt')
state = State(cellsize=5)
old_pose        = Pose(0,0,0)



i = 0
ogm = None
for update in hw.updates():
    if i < 3:
        sys.stdout.write("Processing "+str(update)+'\n')
        sys.stdout.flush()
    if isinstance (update, MotionUpdate):
        state.update(update)
        particle    = state.particles[0]
        ogm = particle.map
        pose = particle.pose
        # ogm.get_cell(old_pose.x, old_pose.y).hasRobot = None

        cell    = ogm.get_cell(pose.x, pose.y)
        cell.hasRobot = pose.dir_str()
        cell.set_log_odds(-INF)
        old_pose = pose
        i+=1
        if i%25 == 0:
            print(ogm)


print(ogm)
