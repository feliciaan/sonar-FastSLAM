import math
import numpy as np

from tuple_utils import tmin, tsub, tmax, tadd

"""
This map keeps track of the occupancies.

To do this, it keeps track of one or more smaller 'SimpleOccupancyGridMap',
which it instantiates as needed. Infinite going left and right is thus
permited, without using to much memory. Indexing is done in a x/y fashion,
where individual cells are 'cellsize'. (0,0) is the cell in the middle of the
first grid.
"""

MAX_SIZE = 300

BLOCKSIZE = 100
CELLSIZE = 5
CELLS_PER_BLOCK = BLOCKSIZE / CELLSIZE
# Precalculated x,y coordinate grid for use in get_cone
COORDINATE_GRID = np.array([[(row * CELLSIZE, col * CELLSIZE)
                                  for row in range(0, MAX_SIZE)]
                                 for col in range(0, MAX_SIZE)])
class OccupancyGridMap:
    """
    Blocksize in centimeters. Blocksize indicate how much is instantiated in
    one go, when out of bounds. Cellsize in centimeters.
    Defaults: blocks of 1m, one cell is 5cm; 400 cells per block
    """

    def __init__(self, copy=False):
        """
        assert blocksize > 1, "invalid blocksize, >1 expected"
        assert cellsize > 0, "invalid cellsize, >0 expected"
        assert blocksize > cellsize, "blocksize should be > cellsize"
        assert blocksize % cellsize == 0, "blocksize should be a multiple of cellsize"
        """
        if not copy:
            # The lowest x,y coordinates, divided by cellsize
            self.minrange = 0, 0
            # The highest x,y coordinate, divided by cellsize
            self.maxrange = int(CELLS_PER_BLOCK), int(CELLS_PER_BLOCK)
            self.grid = np.zeros(shape=self.maxrange)

            # save the robot path by saving all the poses
            # [ Pose @ time 0, Pose @ time 1, ... ]
            self.path = []


            # also create negative blocks, so that we have 4 blocks
            self.get_cell(-1, -1)

    def add_pose(self, pose):
        self.path.append(pose)

    def get_cell(self, x, y):
        """
        Gets the cell at x, y
        Might initialize new blocks if needed, so don't ask things unless needed
        """
        row, col = self._get_cell(x, y)
        return self.grid[row, col]


    def add_to_cell(self, x, y, val):
        row, col = self._get_cell(x, y)
        self.grid[row, col] += val

    def _ensure_coordinates_exist(self, coordinates):
        """
        Check if the x,y coordinates are in the bounds, otherwise increase grid
        :param coordinates: numpy array with indices
        :return: nothing, increases grid if necessary
        """

        if coordinates.size == 0:
            return

        xmin = coordinates[:, 0].min()  # TODO: optimize if necessary
        xmax = coordinates[:, 0].max()
        ymin = coordinates[:, 1].min()
        ymax = coordinates[:, 1].max()

        self._get_cell(xmin, ymin)
        self._get_cell(xmax, ymax)

    def _get_cell(self, x, y):
        """
        Gets the (row, column) coordinates of the cell at x, y (in cm)
        Might modify the array if needed, so don't ask things unless needed.
        """

        row, col = self.cartesian2grid(x, y)


        # Check for out of bounds
        if (row < 0 or col < 0
                or row >= self.grid.shape[0] or col >= self.grid.shape[1]):
            self._increase_grid((row, col))
            # Recalculate with new grid
            return self._get_cell(x, y)

        return row, col

    def _increase_grid(self, out_of_bounds_pos):
        """
        Extends the grid so the row,col coordinates in out_of_bounds_pos
        fall within the grid.
        """
        # get index of block that needs to be added or blocks to keep rectangular shape
        sign_row = math.copysign(1, out_of_bounds_pos[0])
        sign_col = math.copysign(1, out_of_bounds_pos[1])
        new_pos = (int(sign_row * CELLS_PER_BLOCK * math.ceil(abs(sign_row + out_of_bounds_pos[0]) / CELLS_PER_BLOCK)),
                   int(sign_col * CELLS_PER_BLOCK * math.ceil(abs(sign_col + out_of_bounds_pos[1]) / CELLS_PER_BLOCK)))
        new_pos = tadd(self.minrange, new_pos)

        current_size = self.grid.shape
        new_minrange = tmin(self.minrange, new_pos)
        new_maxrange = tmax(self.maxrange, new_pos)

        new_size = tsub(new_maxrange, new_minrange)
        offset = tsub(self.minrange, new_minrange)
        offset_end = tadd(offset, current_size)
        grid = np.zeros(shape=new_size)
        grid[offset[0]:offset_end[0], offset[1]:offset_end[1]] = self.grid

        self.grid = grid
        self.minrange = new_minrange
        self.maxrange = new_maxrange


    def get_cone(self, pose, cone_angle, view_distance):
        """
        Gives cell coordinates in the specified cone.

        Args:
            pose: The coordinates of the apex and the angle of the cone
            cone_angle: The angle (in radians) between the left and right edge
                of the cone
            view_distance: The radius of the cone

        Example cone:
            |       /
            |     /
            |   /
            | /
            +---------
            pose.theta: 45°
            cone_angle = 90° (45° left of theta and 45° right of theta)

        Returns (cell-coordinates array, array of distances to (x,y))
        """

        x, y, theta = pose.x, pose.y, pose.theta
        view_angle = cone_angle / 2
        assert 0 <= view_angle <= math.pi, (
            'A view angle of more then 180° is not permitted; '
            'you gave %s rad.').format(view_angle)

        # TODO: limit bounding box
        xmin = int(x - view_distance - CELLSIZE)
        xmax = int(x + view_distance + CELLSIZE)
        ymin = int(y - view_distance - CELLSIZE)
        ymax = int(y + view_distance + CELLSIZE)
        rowmin, colmin = self.cartesian2grid(xmin, ymin)
        rowmax, colmax = self.cartesian2grid(xmax, ymax)

        grid_size = rowmax - rowmin, colmax - colmin
        coordinates = (COORDINATE_GRID[:grid_size[1], :grid_size[0], :]
                       + (xmin, ymin))
        rel_coords = coordinates - (x, y)

        distances = np.sqrt(np.sum(rel_coords ** 2, axis=2))
        within_view_distance = distances <= view_distance

        angles = np.arctan2(rel_coords[:, :, 1], rel_coords[:, :, 0])
        rel_angles = (angles % (2 * np.pi)) - (theta % (2 * np.pi))
        within_cone_angle = (((-view_angle <= rel_angles)
                              & (rel_angles <= view_angle))
                             | ((-view_angle <= 2 * np.pi - rel_angles)
                                & (2 * np.pi - rel_angles <= view_angle)))

        within_cone = within_view_distance & within_cone_angle

        self._ensure_coordinates_exist(coordinates[within_cone])

        cell_coordinates = self.np_cartesian2grid(coordinates)

        return cell_coordinates[within_cone], distances[within_cone]

    def cartesian2grid(self, x, y):
        row = int(round(y / CELLSIZE)) - self.minrange[0]
        col = int(round(x / CELLSIZE)) - self.minrange[1]
        return row, col

    def np_cartesian2grid(self, coordinates):
        scaled = coordinates[:, :, ::-1] / CELLSIZE
        return np.rint(scaled).astype(np.int) - self.minrange

    def grid2cartesian(self, row, col):
        x = (col + self.minrange[1]) * CELLSIZE
        y = (row + self.minrange[0]) * CELLSIZE
        return x, y

    def in_grid(self,grid_index): #uses row+columns
        return not (grid_index[0] < 0 or grid_index[1] < 0 or grid_index[0] >= self.grid.shape[0] or grid_index[1] >= self.grid.shape[1])

    def __str__(self):
        proc_grid = procentual_grid(self.grid)
        str_grid = np.vectorize(str_cell)(proc_grid)

        # add all poses to map
        for pose in self.path:
            row, col = self._get_cell(pose.x, pose.y)
            str_grid[row, col] = pose.dir_str()

        # add start to map
        str_grid[self._get_cell(0, 0)] = 'X'

        return '\n'.join(''.join(row) for row in str_grid[::-1])

    def __repr__(self):
        return "OccupancyGridMap(blocksize: %dcm, cellsize: %dcm, currentsize: %s)\n%s" % \
               (BLOCKSIZE, CELLSIZE, self.grid.shape, self)



def procentual_grid(grid):
    """Converts a log odds grid to a percentual grid."""
    return 1 - 1 / (1 + np.exp(np.minimum(500, grid)))




def str_cell(cell, chars=" ▁▂▃▄▅▆▇█░"):
    if cell == 0.5:  # 0.5 == unsure about cell
        return chars[-1]
    i = int(cell * (len(chars) - 1))
    return chars[i]
