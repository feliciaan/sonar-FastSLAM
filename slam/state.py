import copy
import random

import motion_model
import sensor_model
from grid_map import OccupancyGridMap
from hardware import MotionUpdate, SensorUpdate
from pose import Pose


RESAMPLE_PERIOD = 10


class State:
    def __init__(self, n_particles=1):
        self.latest_motion = MotionUpdate()
        self.n_particles = n_particles
        self.particles = [Particle(self.n_particles)
                          for _ in range(self.n_particles)]
        self.n_sensor_updates_since_last_resample = 0


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

        # Lowered resampling frequency (p. 109, Thrun)
        self.n_sensor_updates_since_last_resample += 1
        if self.n_sensor_updates_since_last_resample >= RESAMPLE_PERIOD:
            self.resample()
            self.n_sensor_updates_since_last_resample = 0

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

            new_particles.append(self.copy_particle(self.particles[i]))

        self.particles = new_particles

        # TODO add random particles to see if it improves results


    def _normalize_particle_weights(self):
        total_weight = sum(particle.weight for particle in self.particles)
        for particle in self.particles:
            particle.weight /= total_weight


    def best_particle(self):
        return max(self.particles, key=lambda particle: particle.weight)

    def copy_particle(self, old_p):
        p = Particle(self.n_particles, True)
        p.pose = Pose(old_p.pose.x, old_p.pose.y, old_p.pose.theta)
        p.weight = old_p.weight
        p.map.minrange = old_p.map.minrange
        p.map.maxrange = old_p.map.maxrange
        p.map.grid = old_p.map.grid.copy()
        p.map.path = old_p.map.path.copy()

        return p


class Particle:
    def __init__(self, n_particles, copy=False):
        self.map = OccupancyGridMap(copy)
        if not copy:
            x_co=random.gauss(0,0.2)
            y_co=random.gauss(0,0.2)
            theta=random.gauss(0,0.05)
            self.pose = Pose(x_co, y_co, theta)

            self.weight = 1.0 / n_particles

    def update_motion(self, motion, timedelta):
        self.pose = motion_model.calculate_pose(self.pose, motion, timedelta)
        self.map.add_pose(self.pose)

    def update_sensor(self, update):
        self.weight = sensor_model.calc_weight(update, self.pose, self.map)
        sensor_model.update_map(update, self.pose, self.map)
