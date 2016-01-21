import random
import math
from pose import Pose


STD_DEV = .2
THETA_STD_DEV = .05
WHEEL_DISTANCE_IN_CM = 8.4
# FACTOR = 1 / (600 * 50)  # Empirically found
FACTOR = 1 / (600 * 5)  # Empirically found

GAUSSIAN_NOISE = True

# Number of ms per 45 degrees depending on surface ...
MS_PER_45_DEGREES = 200


def calculate_pose(old_pose, motion, timedelta):
    """Calculates a possible new position, with added gaussian noise."""
    
    distance_left = motion.left * timedelta * FACTOR
    distance_right = motion.right * timedelta * FACTOR
    
    if distance_left == distance_right:
        dx = distance_left * math.cos(old_pose.theta)
        dy = distance_left * math.sin(old_pose.theta)
        dtheta = 0
    elif distance_left == -distance_right:
        dx, dy = 0, 0
        #dtheta = timedelta * (math.pi / 4) / MS_PER_45_DEGREES
        dtheta=abs(distance_left)/(WHEEL_DISTANCE_IN_CM/2) #use formula for arc to calculate theta
        if distance_left < distance_right:
            dtheta *= -1
    else: #this never happens right??? 
        assert (True), " |distance_left|  !=  |distance_right|"
        turning_angle = (distance_left - distance_right) / WHEEL_DISTANCE_IN_CM
        polar_length = (distance_left + distance_right) / (2 * turning_angle)
        
        """ not sure this is correct either
        radius_center_robot=(distance_left+distance_right)/(2*turning_angle) #radius of circle from center turninpoint to the middle of the robot
        length_chord=2*radius_center_robot*math.sin(turning_angle/2) #distance traveled center of robot
        dtheta=math.acos(math.sin(turning_angle)*radius_center_robot/length_chord)
        dx=length_chord*math.sin(dtheta)
        dy=length_chord*math.cos(dtheta)
        """
        dx = polar_length * (math.cos(turning_angle) - 1) #not sure this is correct
        dy = polar_length * math.sin(turning_angle) #not sure this is correct
        dtheta = turning_angle

    new_x_with_noise=random.gauss(old_pose.x+dx,STD_DEV) if dx !=0 else old_pose.x
    new_y_with_noise=random.gauss(old_pose.y+dy,STD_DEV) if dy !=0 else old_pose.y
    new_theta_with_noise=random.gauss(old_pose.theta+dtheta,THETA_STD_DEV) if dtheta !=0 else old_pose.theta
    
    #TODO remove? 
    dx_with_noise = random.gauss(dx, STD_DEV) if dx != 0 else 0
    dy_with_noise = random.gauss(dy, STD_DEV) if dy != 0 else 0
    dtheta_with_noise = (random.gauss(dtheta, THETA_STD_DEV)
                         if dtheta != 0 else 0)

    if GAUSSIAN_NOISE:
        return Pose(new_x_with_noise,
                    new_y_with_noise,
                    new_theta_with_noise)
    else:
        new_pose=Pose(old_pose.x + dx,
                    old_pose.y + dy,
                    old_pose.theta + dtheta)
        #print("new pose=",new_pose)
        return new_pose
