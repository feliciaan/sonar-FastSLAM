from hardware import MotionUpdate, SensorUpdate
from grid_map import OccupancyGridMap
import motion_model
# import sensor_model
from pose import Pose


class State:
    def __init__(self, n_particles=1):
        self.latest_motion = MotionUpdate()
        self.n_particles = n_particles
        self.initialize_particles()

    def initialize_particles(self):
        self.particles = [Particle(self.n_particles) for _ in range(self.n_particles)]

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

        self.resample()

    def resample(self):
        # TODO
        pass

class Particle:
    def __init__(self, n_particles):
        self.map = OccupancyGridMap()
        self.pose = Pose(0, 0, 0)
        self.weight = 1.0 / n_particles

    def update_motion(self, motion, timedelta):
        self.pose = motion_model.calculate_pose(self.pose, motion, timedelta)

    def update_sensor(self, update):
        # self.weight = sensor_model.calc_weight(update, self.pose, self.map)
        # sensor_model.update_map(update, self.pose, self.map)
        # TODO re-enab
        pass
