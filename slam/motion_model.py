import random
import math
from pose import Pose


STD_DEV = 2
THETA_STD_DEV = .01
WHEEL_DISTANCE_IN_CM = 8.4

FACTOR = 1 / (600 * 5)  # Empirically found
WHEEL_RADIUS=0.015 #m

GAUSSIAN_NOISE = True

# Number of ms per 45 degrees depending on surface ...
MS_PER_45_DEGREES = 200


#TODO change error parameters to improve result (if using sample motion model)
#error parameters
ERROR1=1#translational error
ERROR2=1#translational error
ERROR3=0.01#angular error
ERROR4=0.01#angular error


def calculate_pose(old_pose, motion, timedelta):
    """Calculates a possible new position, with added gaussian noise."""
    
    distance_left = motion.left * timedelta * FACTOR
    distance_right = motion.right * timedelta *FACTOR
    
    
    if distance_left == distance_right:
        dx = distance_left * math.cos(old_pose.theta)
        dy = distance_left * math.sin(old_pose.theta)
        dtheta = 0
    elif distance_left == -distance_right:
        dx, dy = 0, 0
       # dtheta = timedelta * (math.pi / 4) / MS_PER_45_DEGREES
        dtheta=distance_left/(WHEEL_DISTANCE_IN_CM/2) #left turn results in positive dtheta, uses formula length arc
     

    #TODO replace by motion sample model ?     
    new_x_with_noise=random.gauss(old_pose.x+dx,STD_DEV) if dx !=0 else old_pose.x
    new_y_with_noise=random.gauss(old_pose.y+dy,STD_DEV) if dy !=0 else old_pose.y
    new_theta_with_noise=random.gauss(old_pose.theta+dtheta,THETA_STD_DEV) if dtheta !=0 else old_pose.theta
    
    """
    #TODO remove? 
    dx_with_noise = random.gauss(dx, STD_DEV) if dx != 0 else 0
    dy_with_noise = random.gauss(dy, STD_DEV) if dy != 0 else 0
    dtheta_with_noise = (random.gauss(dtheta, THETA_STD_DEV)
                         if dtheta != 0 else 0)
    """
    if GAUSSIAN_NOISE:
        return Pose(new_x_with_noise,
                    new_y_with_noise,
                    new_theta_with_noise)
    else:
        new_pose=Pose(old_pose.x + dx,
                    old_pose.y + dy,
                    old_pose.theta + dtheta)
        #print("new_pose=",new_pose)
        #print("new pose=",new_pose)
        return new_pose
    """ 
    new_pose=Pose(old_pose.x+dx,old_pose.y+dy,old_pose.theta+dtheta)  
    return sample_motion_model(Pose(0,0,0),Pose(0+dx,0+dy,0+dtheta),old_pose)
     """
   
        
    #TODO fix: doesn't work as it ought to yet
    " implementing algorithm sample motion model odometry  Thrun p136"
def sample_motion_model(old_pose_local,new_pose_local,old_pose_global):
        delta_rot1=math.atan2(new_pose_local.y-old_pose_local.y,new_pose_local.x-old_pose_local.x)-old_pose_local.theta
        delta_trans=math.sqrt((old_pose_local.x-new_pose_local.x)**2+(old_pose_local.y-new_pose_local.y)**2)
        delta_rot2=new_pose_local.theta-old_pose_local.theta-delta_rot1
        
        
        delta_rot1_sample=delta_rot1-sample(ERROR1*delta_rot1**2+ERROR2*delta_trans**2)
        delta_trans_sample=delta_trans-sample(ERROR3*delta_trans**2+ERROR4*delta_rot1**2+ERROR4*delta_rot2**2)
        delta_rot2_sample=delta_rot2-sample(ERROR1*delta_rot2**2+ERROR2*delta_trans**2)
        
        
        x_new=old_pose_global.x+delta_trans_sample*math.cos(old_pose_global.theta+delta_rot1_sample) if(new_pose_local.x !=0) else (old_pose_global.x+new_pose_local.x)
        y_new=old_pose_global.y+delta_trans_sample*math.sin(old_pose_global.theta+delta_rot1_sample) if(new_pose_local.y !=0) else (old_pose_global.y+new_pose_local.y)
        theta_new=old_pose_global.theta+delta_rot1_sample+delta_rot2_sample if(new_pose_local.theta !=0) else (old_pose_global.theta+new_pose_local.theta)
        
        return Pose(x_new,y_new,theta_new)
     
def sample(b_squared):
        return sample_normal_distribution(b_squared)
    
def sample_normal_distribution(b_squared):
        sum=0
        b=math.sqrt(b_squared)
        for i in range(0,12):
            sum+=random.uniform(-1*b,b)
        return 1/2*sum  
        
    