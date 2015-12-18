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
    i+=1
    if i % 100 == 0:
        print(ogm)
        time.sleep(update.timedelta/1000)
        break;
