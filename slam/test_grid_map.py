"""
Walks through the grid map, in a very naive way
"""

from grid_map import OccupancyGridMap, Cell
from hardware import *
from pose import Pose
from motion_model import calculate_pose
from state import State
import math

ogm = OccupancyGridMap(cellsize = 25)
ogm.getCell(0,0).hasRobot = '↦'
state = State()
old_pose        = Pose(0,0,0)



i = 0
for update in updates('../test/test6.txt'):
    if isinstance(update, MotionUpdate):
        print("\n---------------\n")
        print(state.latest_motion)
        print(update.timedelta)
        state.update(update)
        pose = state.particles[0].pose
        ogm.getCell(old_pose.x, old_pose.y).hasRobot = None
        ogm.getCell(pose.x, pose.y).hasRobot = pose.dir_str()
        old_pose = pose
        print(pose)
        print(ogm)
        i += 1
        if (i > 100):
            break
