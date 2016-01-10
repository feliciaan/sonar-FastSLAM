import time
from grid_map import OccupancyGridMap
from hardware import *
from pose import Pose
from motion_model import calculate_pose
from state import State
from settings import DEBUG
import math
from grid_world import *
import pickle

INF = 500

hw = Hardware("../test/testdata-film-feli01.txt")
state = State(n_particles=1, cellsize=5, blocksize=100)

old_pose = Pose(0, 0, 0)

ogm = None
print_next = False


for update in hw.updates():
    start_time = time.time()
    state.update(update)
    particle = state.particles[0]
    ogm = particle.map
    pose = particle.pose

    old_pose = pose

    tmp = update.__str__()

    if print_next:
        ms = update.__str__().split('Timedelta')[1][2:-1]
        degrees = pose.__str__()
        # print(i, ', ms:', ms, ', degrees:', degrees)
        print(degrees)
        # input number + ms + degrees

        pickle.dump(ogm.__str__(), open("gridworld.pkl", "wb"))
        with open("out.txt", "a") as myfile:
            # draw a world
            # gw.update_gridworld(ogm.__str__())

            # input("Enter to continue")
            myfile.write(pose.__str__() + '\n')

            myfile.write(ogm.__str__() + '\n')
        print_next = False

    if 'MotionUpdate(Left: 300	Right: -300' in tmp \
            or 'MotionUpdate(Left: -300	Right: 300' in tmp:
        print_next = True

stop_time = time.time()

# ogm.set_robot_path(robot_poses)

print("elapsed time : ", (stop_time - start_time) * 1000)
with open("out.txt", "a") as myfile:
    myfile.write(ogm.__str__())
