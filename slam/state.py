import random
from joblib import Parallel, delayed

import motion_model
import sensor_model
from grid_map import OccupancyGridMap
from hardware import MotionUpdate, SensorUpdate
from pose import Pose


class State:
    def __init__(self, n_particles=1, cellsize=5, blocksize=100):
        self.latest_motion = MotionUpdate()
        self.n_particles = n_particles
        self.particles = [Particle(self.n_particles, cellsize, blocksize) for _ in range(self.n_particles)]

    def update(self, update):
        if isinstance(update, MotionUpdate):
            self.update_motion(update)
        elif isinstance(update, SensorUpdate):
            self.update_sensor(update)

    def update_motion(self, update):
        for particle in self.particles:
            particle.update_motion(self.latest_motion, update.timedelta)

        self.latest_motion = update

    def update_sensor(self, update):
        for particle in self.particles:
            particle.update_motion(self.latest_motion, update.timedelta)
            particle.update_sensor(update)

        #Parallel(n_jobs=4)(delayed(Particle.update_sensor)(particle, update) for particle in self.particles)

        self.resample()

    def resample(self):
        """Implements algorithm Low_variance_sampler (Thrun, p. 110)"""

        self._normalize_particle_weights()

        new_particles = []

        r = random.random() / self.n_particles
        c = self.particles[0].weight
        i = 0
        for m in range(self.n_particles):
            u = r + m / self.n_particles
            while u > c:
                i += 1
                c += self.particles[i].weight
            new_particles.append(self.particles[i])

        self.particles = new_particles

    def _normalize_particle_weights(self):
        total_weight = sum(particle.weight for particle in self.particles)
        for particle in self.particles:
            particle.weight /= total_weight


class Particle:
    def __init__(self, n_particles, cellsize, blocksize):
        self.map = OccupancyGridMap(blocksize = blocksize, cellsize = cellsize)
        self.pose = Pose(0, 0, 0)
        self.weight = 1.0 / n_particles

    def update_motion(self, motion, timedelta):
        self.pose = motion_model.calculate_pose(self.pose, motion, timedelta)

    def update_sensor(self, update):
        self.weight = sensor_model.calc_weight(update, self.pose, self.map)
        sensor_model.update_map(update, self.pose, self.map)
