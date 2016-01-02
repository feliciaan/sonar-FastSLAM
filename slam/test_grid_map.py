"""
Walks through the grid map, in a very naive way
"""
import time

from hardware import Hardware
from state import State

hardware = Hardware("../test/testdata-film-feli01.txt")
state = State(n_particles=50, cellsize=5, blocksize=100)

sumdeltas = 0

for update in hardware.updates():
    start_time = time.time()
    state.update(update)
    stop_time = time.time()

    timedeltadelta = update.timedelta - (stop_time - start_time) * 1000
    sumdeltas += timedeltadelta

    if timedeltadelta < 0:
        print("Slower than updates: %f, current delay %f" % (timedeltadelta, sumdeltas))
    else:
        print("Faster than updates: %f, current delay %f" % (timedeltadelta, sumdeltas))

print(sumdeltas)
best_particle = max(state.particles, key=lambda particle: particle.weight)
print(repr(best_particle.map))
