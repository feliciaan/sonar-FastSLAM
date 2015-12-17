from hardware import MotionUpdate, SensorUpdate
from grid_map import OccupancyGridMap
import motion_model
import sensor_model

N_PARTICLES = 100


class State:
    def __init__(self):
        self.latest_motion = None
        self.initialize_particles()

    def initialize_particles(self):
        self.particles = [Particle() for _ in range(N_PARTICLES)]

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
    def __init__(self):
        self.map = OccupancyGridMap()
        self.pose = Pose(self.map.width / 2, self.map.height / 2, 0)
        self.weight = 1.0 / N_PARTICLES

    def update_motion(self, motion, timedelta):
        self.pose = motion_model.calculate_pose(self.pose, motion, timedelta)

    def update_sensor(self, update):
        self.weight = sensor_model.calc_weight(update, self.pose, self.map)
        sensor_model.update_map(update, self.pose, self.map)


class Pose:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
