"""
Walks through the grid map, in a very naive way
"""
import time
import pickle

from hardware import Hardware
from state import State


hardware = Hardware(serial_port='/dev/tty.HC-06-DevB', output_file="../test/testdata-film03.txt")
state = State(n_particles=10, cellsize=5, blocksize=100)


sumdeltas = 0

start = time.time()
i = 0
for update in hardware.updates():
    i += 1
    start_time = time.time()
    state.update(update)
    stop_time = time.time()

    timedeltadelta = update.timedelta - (stop_time - start_time) * 1000
    sumdeltas += timedeltadelta

    if timedeltadelta < 0:
        print("Slower than updates: %f, current delay %f" % (timedeltadelta, sumdeltas))
    else:
        print("Faster than updates: %f, current delay %f" % (timedeltadelta, sumdeltas))

    if i % 100:
        with open("gridworld.pkl", "wb") as f:
            best_particle = state.best_particle()
            pickle.dump(str(best_particle.map), f)
            
print(sumdeltas)
stop = time.time()
print("elapsed time : ", (stop - start) * 1000)
with open("gridworld.pkl", "wb") as f:
    best_particle = state.best_particle()
    pickle.dump(str(best_particle.map), f)
