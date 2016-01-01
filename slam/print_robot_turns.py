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
state = State(n_particles=1, cellsize=5, blocksize=100)

old_pose = Pose(0, 0, 0)

i = 0
ogm = None
print_next = False

robot_headings = []
robot_poses = []
for update in hw.updates():
    start_time = time.time()
    state.update(update)
    particle = state.particles[0]
    ogm = particle.map
    pose = particle.pose

    robot_headings.append(pose.dir_str())
    robot_poses.append(ogm.gridcell_position(pose.x, pose.y))

    # with open("out.txt", "a") as myfile:
    #     myfile.write(pose.__str__() + '\n')
    #
    #     myfile.write(ogm.__str__())
    #
    # print('Until first measurement ....')
    # exit()

    cell = -INF
    old_pose = pose
    i += 1

    tmp = update.__str__()

    if print_next:
        ms = update.__str__().split('Timedelta')[1][2:-1]
        degrees = (pose.__str__().split('θ')[2][1:])
        # print(i, ', ms:', ms, ', degrees:', degrees)
        print(degrees)
        # input number + ms + degrees


        # save the information for the robot path
        ogm.set_robot_path(robot_poses)
        ogm.set_robot_path_headings(robot_headings)

        with open("out.txt", "a") as myfile:
            myfile.write(pose.__str__() + '\n')

            myfile.write(ogm.__str__())
        print_next = False

        # print('Until first turn ....')
        # exit()

    if 'MotionUpdate(Left: 300	Right: -300' in tmp \
            or 'MotionUpdate(Left: -300	Right: 300' in tmp:
        print_next = True

stop_time = time.time()

print(robot_poses)
print(robot_headings)
ogm.set_robot_path(robot_poses)

print("elapsed time : ", (stop_time - start_time) * 1000)
with open("out.txt", "a") as myfile:
    myfile.write(ogm.__str__())
