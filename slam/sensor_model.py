import math
import scipy.spatial
from pose import Pose
from tuple_utils import  tsub

MAX_RANGE = 100  # In cm
CONE_ANGLE = 0.872664626  # In radians
PROBABILITY_FREE = 0.0001
RECOGNITION_SENSITIVITY = 5  # In cm


def calc_weight(measurements, pose, map_):
    probability = 1
    #return probability # TODO remove
    
    
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
    
        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)
        # TODO: what if no expected distance is known? Fixed -> weight
      
        """if measured_dist is None:
            if expected_distance > MAX_RANGE:
                # It's correct as far as we know; our sensor doesn't go this
                # far. Just ignore this sensor for all particles.
                continue
            else:
                measured_dist = MAX_RANGE
        """     
        
        """likelihoods filed range finder, p172"""
        if measured_dist is not None and measured_dist < MAX_RANGE:#discard max range readings
            #coordinates of endpoint measured distance
            x_co=sensor_pose.x+measured_dist*math.cos(sensor_pose.theta)
            y_co=sensor_pose.y+measured_dist*math.sin(sensor_pose.theta)
            
            #when sensor measurement falls into unknown category, prob is assumed constant p173
            measured_cell_occupancy=check_for_unknown(map_,(x_co,y_co))
                           
            if measured_cell_occupancy=="unknown":
                probability*=1/MAX_RANGE
                                
            #find nearest neighbour that is occupied    
            elif measured_cell_occupancy=="known":   
                nearest_object = find_nearest_neighbor(map_, (x_co,y_co))
                if nearest_object is not None:
                     #calculate Euclidean distance between measured coord and closest occupied coord
                    sub=tsub((x_co,y_co),nearest_object)
                    expected_distance=math.hypot(sub[0],sub[1])
                    probability*=_prob_of_distances(expected_distance,0.0)
       
            #distance_to_closest_object_in_cone(map_,sensor_pose, CONE_ANGLE, MAX_RANGE)
    
    """
        if measured_dist is None :
            if expected_distance > MAX_RANGE:
                
                continue
            else:
                # We'll assume we measured something at the maximum measurable
                # range.
                measured_dist = MAX_RANGE
        
            probability *= _prob_of_distances(measured_dist, expected_distance)
        """
    return probability



      
#if measured_distance fall into unknown category, cell get different probability, no need to
#find nearest occupied cell      
def check_for_unknown(map,position):
    grid_index=map.cartesian2grid(position[0],position[1])  
    if (not map.in_grid(grid_index)):
        return "unknown"
    cell=map.get_cell(position[0],position[1])
    if cell==0.5:
        return "unknown"
    else:
        return "known"
 
def find_nearest_neighbor(map,position): 
    #find nearest occupied cell
    cell=map.get_cell(position[0],position[1])
    #measured cell is occupied
    if cell==0.5:
        return position
    else:
        grid_index=map.cartesian2grid(position[0],position[1])
        distance=1
        #check in radius around current position, using (row,column) positions in grid 
        #if counter is 0, no occupied positions inside the grid have been found, return None  
        counter=-1
        while counter!=0:
            counter=0
            for i in range(0,distance+1,1):
                for a in (-1,1):
                    for b in (-1,1):
                        pos=(grid_index[0]+a*distance,grid_index[1]+b*i)
                        if(map.in_grid(pos)):
                            if map.grid[pos[0],pos[1]]>0.6:
                                counter+=1
                                return map.grid2cartesian(pos[0],pos[1])
                                
                        pos=(grid_index[0]+a*i,grid_index[1]+b*distance)
                        if(map.in_grid(pos)):
                            if map.grid[pos[0],pos[1]]>0.6:
                                counter+=1
                                return map.grid2cartesian(pos[0],pos[1]) 
                         
            distance+=1
        return None 
                  
                
        
        
        
        
    """
    if (position[0]<map.minrange[0] or position[0]> map.maxrange[0] or position[1] <map.minrange[1] or position[1]>map.maxrange[1]):
        return None
    
    cell=map.get_cell(position[0],position[1])
    if cell>0.5: #occupied
        return (position[0],position[1])
    else: #look untill occupied cell is found
         next_position=(position[0]+math.cos(pose_angle)*map.cellsize,position[1]+math.sin(pose_angle)*map.cellsize)
         return (find_nearest(map,next_position,pose_angle))
    """
    
    
    

def distance_to_closest_object_in_cone(map, pose, cone_width_angle, max_radius):
        """
        Raytraces until a first object is found. Does not search further then max_radius.
        Keep max_radius quite small (e.g. 130cm or 200cm), as it will get slow otherwise.

        Returns the pareto-front of (distance, log_odds). None-values are ignored
        """

        cells = map.get_cone(pose, cone_width_angle, max_radius)

        """def snd(tupl):
            (x, y) = tupl
            return y
"""
        cells = list(cells)
        cells.sort(key=snd)

        found = []
        curr_max = -1
        for (cell, d) in cells:
            cell = map.get_cell(*cell)
            if cell == 0.5:
                continue
            if cell > curr_max:
                curr_max = cell
                found.append((d, cell))

        return found



def _prob_of_distances(measured, expected):
    return _normal_distribution(measured, expected, RECOGNITION_SENSITIVITY)


def _normal_distribution(x, mean, stddev):
    denominator = (math.sqrt(2 * math.pi) *
                   stddev *
                   math.exp(((x - mean) ** 2) / (2 * (stddev ** 2))))
    return 1 / denominator


def update_map(measurements, pose, map_):
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        measurement = True
        if measured_dist is None or measured_dist > MAX_RANGE:
            measured_dist = MAX_RANGE
            measurement = False

        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)

        cell_coordinates, distances = map_.get_cone(sensor_pose, CONE_ANGLE,
                                                    measured_dist)

        cutoff = measured_dist * 0.8
        empty_coords = cell_coordinates[distances < cutoff]
        non_empty_coords = cell_coordinates[distances > cutoff]

        map_.grid[empty_coords[:, 0], empty_coords[:, 1]] += _log_odds(PROBABILITY_FREE)
        if measurement and len(non_empty_coords) > 0:
            non_empty_log_odds = _log_odds(.5 + (.5 / (len(non_empty_coords) + 1)))
            map_.grid[non_empty_coords[:, 0], non_empty_coords[:, 1]] += non_empty_log_odds


def _measurement_per_angle(measurements):
    return [
        (math.pi / 2, measurements.left),
        (0, measurements.front),
        (-math.pi / 2, measurements.right),
    ]


def _log_odds(p):
    return math.log(p / (1 - p))
