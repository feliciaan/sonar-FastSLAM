"""
Walks through the grid map, in a very naive way
"""
import time
import pickle

from hardware import Hardware
from state import State


hardware = Hardware("../test/ms2_triple_1.txt")
# /dev/tty.HC-06-DevB
#
# hardware = Hardware(serial_port='/dev/rfcomm0', output_file='../test/ms2_triple_1.txt', testfile='../test/test.txt')
state = State(n_particles=150)


sumdeltas = 0
current_time = 0
start = time.time()
i = 0
for update in hardware.updates():
    i += 1
    start_time = time.time()
    state.update(update)
    stop_time = time.time()

    current_time += update.timedelta
    timedeltadelta = update.timedelta - (stop_time - start_time) * 1000
    sumdeltas += timedeltadelta

    if timedeltadelta < 0:
        #print("Slower than updates: %f, current delay %f" % (timedeltadelta, sumdeltas))
        None
    else:
        #print("Faster than updates: %f, current delay %f" % (timedeltadelta, sumdeltas))
        None
    if i % 250:
        with open("gridworld.pkl", "wb") as f:
            best_particle = state.best_particle()
            pickle.dump([str(best_particle.map), current_time], f)
            # print(str(best_particle.map))

print(sumdeltas)
stop = time.time()
print("elapsed time : ", (stop - start) * 1000)
with open("gridworld.pkl", "wb") as f:
    best_particle = state.best_particle()
    pickle.dump([str(best_particle.map), current_time], f)
    # print(str(best_particle.map))
