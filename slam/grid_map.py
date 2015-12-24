from itertools import product
import math
import numpy as np

from tuple_utils import tmin, tsub, tmax, tadd

"""
This map keeps track of the occupancies.
To do this, it keeps track of one or more smaller 'SimpleOccupancyGridMap', which it instantiates as needed.
Infinite going left and right is thus permited, without using to much memory.
Indexing is done in a x/y fashion, where individual cells are 'cellsize'.
(0,0) is the cell in the middle of the first grid
"""

PRECALCULATED_GRID = np.array([[(i, j) for i in range(0, 300)] for j in range(0, 300)])

class OccupancyGridMap:
    """
    Blocksize in centimeters. Blocksize indicate how much is instantiated in one go, when out of bounds.
    Cellsize in centimeters.
    Defaults: blocks of 1m, one cell is 5cm; 400 cells per block
    """

    def __init__(self, blocksize=100, cellsize=5):
        assert blocksize > 1, "invalid blocksize, >1 expected"
        assert cellsize > 0, "invalid cellsize, >0 expected"
        assert blocksize > cellsize, "blocksize should be > cellsize"
        assert blocksize % cellsize == 0, "blocksize should be a multiple of cellsize"
        self.blocksize = blocksize
        self.cellsize = cellsize
        self.cells_per_block = self.blocksize/self.cellsize
        self.minrange = (0, 0)  # (x,y)
        self.maxrange = (self.cells_per_block, self.cells_per_block)  # (x,y)
        self.grid = np.zeros(shape=self.maxrange)

        # also create negative blocks, so that we have 4 blocks
        self.get_cell(-1,-1)

    def _debug(self):
        print("Grid size:\t(%d,%d)\nMin Range:\t(%d,%d)\nMax Range:\t(%d,%d)" %
              (self.grid.shape[0], self.grid.shape[1],
               self.minrange[0], self.minrange[1],
               self.maxrange[0], self.maxrange[1]))

    def get_cell(self, x, y):
        """
        Gets the cell at x, y
        Might initialize new blocks if needed, so don't ask things unless needed
        """
        row, col = self._get_cell(x, y)
        return self.grid[row, col]

    def add_to_cell(self, x, y, val):
        row, col = self._get_cell(x, y)
        self.grid[row, col] = val

    def _get_cell(self, x, y):
        """
        Gets the cell at x, y (in cm)
        Might modify the array if needed, so don't ask things unless needed
        """
        # save orignal values
        old_x, old_y = x, y

        # get cell
        x /= self.cellsize
        y /= self.cellsize

        # get correct x and y cell values
        x -= self.minrange[0]
        y -= self.minrange[1]

        # check out of bounds
        if x < self.minrange[0] or y < self.minrange[1] or x > self.maxrange[0] or y > self.maxrange[1]:
            self._increase_grid((x, y))
            # x and y values are possibly changed (offset is different)
            return self._get_cell(old_x, old_y)

        return x, y

    def _increase_grid(self, out_of_bounds_pos):
        # get index of block that needs to bed added or blocks to keep rectangular shape
        signx = math.copysign(1, out_of_bounds_pos[0])
        signy = math.copysign(1, out_of_bounds_pos[1])
        new_pos = (signx * self.cells_per_block*math.ceil(abs((1 + out_of_bounds_pos[0]))/self.cells_per_block),
                   signy * self.cells_per_block*math.ceil(abs((1 + out_of_bounds_pos[1]))/self.cells_per_block))

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

    def distance_to_closest_object_in_cone(self, pose, cone_width_angle, max_radius):
        """
        Raytraces until a first object is found. Does not search further then max_radius.
        Keep max_radius quite small (e.g. 130cm or 200cm), as it will get slow otherwise.

        Returns the pareto-front of (distance, log_odds). None-values are ignored
        """
        # TODO: plz implement me
        cells = self.get_cone(pose, cone_width_angle, max_radius)

        def snd(tupl):
            (x, y) = tupl
            return y

        cells = list(cells)
        cells.sort(key=snd)

        found = []
        curr_max = -1
        for (cell, d) in cells:
            cell = self.get_cell(*cell)
            if cell == 0.5:
                continue
            if cell > curr_max:
                curr_max = cell
                found.append((d, cell))

        return found

    def get_cone(self, pose, cone_angle, radius):
        """
        Gives cell in the cone, where x,y is the position, theta is the look direction and angle is how much is visible left/right.
        Angle in radians; this value is the view to the left.

        |       /
        |     /
        |   /
        | /
        +---------
        Theta: 45°; angle = 45° as we can see 45° left and 45° to the right, for a total of 90°
        Return (cell, distance to x,y)
        """
        x, y, view_distance, theta, view_angle = pose.x, pose.y, radius, pose.theta, cone_angle / 2
        assert view_angle <= math.pi, "A view angle of more then 180° is not permitted, you gave " + str(view_angle)
        xmin = int(x - view_distance - self.cellsize)
        xmax = int(x + view_distance + self.cellsize)
        ymin = int(y - view_distance - self.cellsize)
        ymax = int(y + view_distance + self.cellsize)

        indices = PRECALCULATED_GRID[: (xmax - xmin)/self.cellsize, : (ymax - ymin)/self.cellsize, :] * self.cellsize + ymin

        temp = indices - (x, y)
        dist = np.sqrt(np.sum(temp ** 2, axis=2))
        s_dist = dist.copy()
        dist[dist < view_distance] = 1
        dist[dist > view_distance] = 0

        angle = (np.arctan2(temp[:, :, 0], temp[:, :, 1]) + np.pi) - theta
        angle[~(((-view_angle <= angle) & (angle <= view_angle)) | ((-view_angle + 2 * np.pi < angle) &
                                                                    (angle < view_angle + 2 * np.pi)))] = 0
        angle[~(angle == 0.0)] = 1

        comb = np.minimum(dist, angle)
        d = np.where(comb == 1)

        for e in np.transpose(d):
            yield (indices[e[0], e[1]], s_dist[e[0], e[1]])

    def build_str(self):
        result = ""

        proc_grid = procentual_grid(self.grid)
        for row in proc_grid:
            for col in row:
                result += str_cell(col)
                #if (x, y) == (0, 0):
                #        orig_repr = str_cell(procentual_grid(self.get_cell(0, 0)), chars="○◎◍◒◕●◙◌");
                #        reprs[-1] = orig_repr + reprs[-1][1:]
            result += "\n"

        return "GridMap(blocksize: %dcm, cellsize: %dcm, currentsize: %s)\n%s" % \
               (self.blocksize, self.cellsize, self.grid.shape, result)

    def __str__(self):
        return self.build_str()


def procentual_grid(grid):
    return 1 - 1 / (1 + np.exp(np.minimum(500, grid)))


def str_cell(cell, chars=" ▁▂▃▄▅▆▇█░"):
    if cell == 0.5:  # 0.5 == unsure about cell
        return chars[-1]
    i = int(cell * (len(chars) - 1))
    return chars[i]
