"""
Walks through the grid map, in a very naive way
"""
import time
from grid_map import OccupancyGridMap, Cell
from hardware import *
from pose import Pose
from motion_model import calculate_pose
from state import State
import math

hw  = Hardware('../test/nieuwedata2.txt')
ogm = OccupancyGridMap(cellsize = 5)
ogm.getCell(0,0).hasRobot = '↦'
state = State()
old_pose        = Pose(0,0,0)

print(ogm)

i = 0
for update in hw.updates():
    if isinstance(update, MotionUpdate):
        # print("\n---------------\n")
        # print(state.latest_motion)
        # print(update.timedelta)
        state.update(update)
        pose = state.particles[0].pose
        # ogm.getCell(old_pose.x, old_pose.y).hasRobot = None
        cell    = ogm.getCell(pose.x, pose.y)
        cell.hasRobot = pose.dir_str()
        cell.set(0)
        old_pose = pose
        # print(pose)
        print(ogm)
        i += 1
        time.sleep(update.timedelta/1000)
