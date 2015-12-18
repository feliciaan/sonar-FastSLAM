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

hw  = Hardware('../test/nieuwedata2.txt')
ogm = OccupancyGridMap(cellsize = 5)
ogm.get_cell(0,0).hasRobot = '↦'
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
        ogm.get_cell(old_pose.x, old_pose.y).hasRobot = None
        cell    = ogm.get_cell(pose.x, pose.y)
        cell.hasRobot = pose.dir_str()
        cell.set_log_odds(-INF)
        old_pose = pose
        # print(pose)

        cells = ogm.cells_between(pose.x, pose.y, 50, pose.theta, math.pi * 180 / 180)
        cells = list(cells)
        for (cell, d) in cells:
            if 44 < d < 50:
                cell.set_log_odds(INF)
            else:
                cell.set_log_odds(0.2)


        print(ogm)
        for (cell, d) in cells:
            cell.set_log_odds(-INF)
        i += 1

        time.sleep(update.timedelta/100)
