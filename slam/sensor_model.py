import math
from pose import Pose
from tuple_utils import  tsub
from grid_map import procentual_grid

MAX_RANGE = 150  # In cm
CONE_ANGLE = 0.872664626  # In radians
PROBABILITY_FREE = 0.00001
RECOGNITION_SENSITIVITY = 5 # In cm


def calc_weight(measurements, pose, map_):
    probability = 1
    #return probability
        
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        # TODO: Pose of sensor is simplified to pose of robot
        sensor_pose = Pose(pose.x, pose.y, pose.theta + sensor_angle)
        
        # TODO: what if no expected distance is known? Fixed -> weight
               
        """likelihoods fields range finder, p172"""
        if measured_dist is not None and measured_dist < MAX_RANGE:#discard max range readings
            
            #coordinates of endpoint measured distance
            x_co=sensor_pose.x+measured_dist*math.cos(sensor_pose.theta)
            y_co=sensor_pose.y+measured_dist*math.sin(sensor_pose.theta)
           
            nearest_object = find_nearest_neighbor(map_, (x_co,y_co))
            #when sensor measurement falls into unknown category, prob is assumed constant p173               
            if nearest_object=="unknown":
                probability*=1/MAX_RANGE
                                
            #find nearest neighbour that is occupied    
            elif nearest_object is not None: 
                #calculate Euclidean distance between measured coord and closest occupied coord
                sub=tsub((x_co,y_co),nearest_object)
                distance=math.hypot(sub[0],sub[1])
                prob=_prob_of_distances(distance,0.0)
                probability*=prob
    
     
    return probability


"""
   value cell calculated as a value between 0 and 1
"""
def proc_value_cell(cell):
    proc_value= 1-1/(1+math.exp(min(500,cell))) #procentual value
    return proc_value

"""
finds nearest occupied cell for cell with given position
    if the position is outside the grid, the cell is unknown
    if the cell is inside the grid but has value 0.5, the cell is unknown
    if the cell has value 1, the cell itself is occupied, return cell
        otherwise look for nearest occupied neighbour--> use grid coord (row,column) and circle around cell with increasing distance
        occupied cell found if value ==1 

"""
def find_nearest_neighbor(map,position):
    grid_index=map.cartesian2grid(position[0],position[1])  
    if (not map.in_grid(grid_index)):
        return "unknown" 
    
    cell=map.get_cell(position[0],position[1])
    if proc_value_cell(cell)==0.5: 
        return "unknown"
    
    #measured cell is occupied
    if proc_value_cell(cell)==1: 
        return position
    else:
        
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
                            if proc_value_cell(map.grid[pos[0],pos[1]])==1:
                                counter+=1
                                return map.grid2cartesian(pos[0],pos[1])
                                
                        pos=(grid_index[0]+a*i,grid_index[1]+b*distance)
                        if(map.in_grid(pos)):
                            if proc_value_cell(map.grid[pos[0],pos[1]])==1:
                                counter+=1
                                return map.grid2cartesian(pos[0],pos[1]) 
                         
            distance+=1
        return None 
                  
      

def distance_to_closest_object_in_cone(map, pose, cone_width_angle, max_radius):
        """
        Raytraces until a first object is found. Does not search further then max_radius.
        Keep max_radius quite small (e.g. 130cm or 200cm), as it will get slow otherwise.

        Returns the pareto-front of (distance, log_odds). None-values are ignored
        """

        cells = map.get_cone(pose, cone_width_angle, max_radius)
        map.grid=procentual_grid(map.grid)
        def snd(tupl):
            (x, y) = tupl
            return y

        cells = list(cells)
        cells.sort(key=snd)

        found = []
        curr_max = -1
        for (cell, d) in cells:
            cell = map.get_cell(*cell)
            if math.floor(cell*10) == 5:
                continue
            if cell > curr_max:
                curr_max = cell
                found.append((d, cell))

        return found



def _prob_of_distances(measured, expected):
    return _normal_distribution(measured, expected, RECOGNITION_SENSITIVITY)


def _normal_distribution(x, mean, stddev):
    den=(math.sqrt(2*math.pi)*stddev)
    return  1/den*math.exp((-1*((x-mean)**2))/(2*(stddev**2)))
    


def update_map(measurements, pose, map_):
    for sensor_angle, measured_dist in _measurement_per_angle(measurements):
        measurement = True
        if measured_dist is None or measured_dist >= MAX_RANGE:
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
