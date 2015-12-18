import math
from cell import Cell
"""
This map keeps track of the occupancies.
To do this, it keeps track of one or more smaller 'SimpleOccupancyGridMap', which it instantiates as needed.
Infinite going left and right is thus permited, without using to much memory.
Indexing is done in a x/y fashion, where individual cells are 'cellsize'.
(0,0) is the cell in the middle of the first grid
"""
class OccupancyGridMap:
    """
    Blocksize in centimeters. Blocksize indicate how much is instantiated in one go, when out of bounds.
    Cellsize in centimeters.
    Defaults: blocks of 1m, one cell is 5cm; 400 cells per block
    """
    def __init__(self, blocksize=100, cellsize=5):
        assert blocksize > 1, "invalid blocksize, >1 expected"
        assert cellsize > 0, "invalid cellsize, >1 expected"
        assert blocksize > cellsize, "blocksize should be > cellsize"
        assert blocksize % cellsize == 0, "blocksize should be a multiple of cellsize"
        self.blocksize = blocksize
        self.cellsize = cellsize
        self.cellsPerSmaller = int(blocksize / cellsize)
        self.smallmaps = dict()
        self.xrange = (0,0)
        self.yrange = (0,0)
        init_kwadrants  = [(0,0)]
        for (x,y) in init_kwadrants:
            self._init_map(x, y)


    def _init_map(self, x, y):
        sogm    = SimpleOccupancyGridMap(self.cellsPerSmaller, self.cellsPerSmaller)
        self.smallmaps[(x,y)] = sogm

    """
    Gets the cell at x, y
    Might initialize new blocks if needed, so don't ask things unless needed
    """
    def get_cell(self, x, y):
        # get smaller map
        xi = int( x // self.blocksize)
        yi = int( y // self.blocksize)
        if (xi, yi) not in self.smallmaps:
            self._init_map(xi,yi)
            (xmin, xmax)    = self.xrange
            self.xrange     = (min(xmin, xi), max(xmax, xi) )
            (ymin, ymax)    = self.yrange
            self.yrange     = (min(ymin, yi), max(ymax, yi) )

        smallmap = self.smallmaps[(xi,yi)]

        # get the coordinates in the smaller map
        xd  = x % self.blocksize
        yd  = y % self.blocksize
        xd  = int(math.floor( xd / self.cellsize))
        yd  = int(math.floor( yd / self.cellsize))
        row = yd
        col = xd
        return smallmap.get_cell(row,col)

    def distance_to_closest_object_in_cone(self, pose, cone_width_angle):
        # TODO: plz implement me
        pass


    def get_cone(self, pose, cone_angle, radius):
        return self._cells_in_cone(pose.x, pose.y, radius, pose.theta, cone_angle/2)
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
    def _cells_in_cone(self, x, y, view_distance, theta, view_angle):
        assert view_angle <= math.pi, "A view angle of more then 180° is not permitted, you gave "+str(view_angle)
        xmin = int(x - view_distance - self.cellsize)
        xmax = int(x + view_distance + self.cellsize)
        ymin = int(y - view_distance - self.cellsize)
        ymax = int(y + view_distance + self.cellsize)


        for xi in range(xmin, xmax, int(self.cellsize//2)):
            for yi in range(ymin, ymax, int(self.cellsize//2)):
                d = distance(x,y,xi,yi)
                if d > view_distance:
                    continue
                anglei  = angle(xi,yi,x,y) - theta  # [-theta, 2*pi - theta]
                # view_angle    : [0, pi]
                if not ((-view_angle <= anglei <= view_angle) or (-view_angle <= anglei - 2*math.pi <= view_angle )):
                    continue
                cell    = self.get_cell(xi, yi)
                yield (cell, d)



    def build_str(self, border=False):
        (ymin, ymax)    = self.yrange
        (xmin, xmax)    = self.xrange
        result  = ""
        cellsPerSmaller = self.cellsPerSmaller + (2 if border else 0)
        emptyRepr   = ["░" * cellsPerSmaller] * cellsPerSmaller
        for y in range(ymax, ymin-1, -1):
            lines = [""] * (cellsPerSmaller)
            for x in range(xmin, xmax+1):
                reprs   = emptyRepr
                if (x,y) in self.smallmaps:
                    reprs = self.smallmaps[(x,y)].build_str(reverse=True, border = border, borderMsg = str((x,y)))
                    if (x,y) == (0,0):
                        orig_repr   = self.get_cell(0,0).origin_str();
                        reprs[-1] = orig_repr + reprs[-1][1:]

                for i in range(0, cellsPerSmaller):
                    lines[i] = lines[i] + reprs[i]
            result += "\n" + "\n".join(lines)

        return ("GridMap with blocksize "+str(self.blocksize)+"cm and resolution "+str(self.cellsize)+"cm:\n"+ result)


    def __str__(self):
        return self.build_str()

def distance(x0,y0,x1,y1):
    return math.sqrt( (x0 - x1)**2 + (y0 - y1)**2 )

"""
Returns the angle between the two coordinates, expressed in [0,2*pi]
"""
def angle(x0,y0,x1,y1):
    dx = x0 - x1
    dy = y0 - y1
    return (2*math.pi + math.atan2(dy, dx)) % (2*math.pi)


"""
Simple occupancy grid map. uses row/col (height/width) indexing, stargint in the upper left corner.
Uses ints as indices
"""
class SimpleOccupancyGridMap:
    def __init__(self, height, width):
        self.width = width
        self.height = height
        """
        Grid[ROW][HEIGHT]
        """
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        for rowi in range(0,height):
            for coli in range(0,width):
                self.grid[rowi][coli] = Cell()


    def __iter__(self):
        return iter(self.grid)


    def __repr__(self):
        return str(self)

    def build_str(self, reverse=False, border=False, borderMsg = ""):
        borderMsg   = " "+borderMsg+" "
        res = ["╔" + borderMsg + ('═' * (self.width - len(borderMsg))) + "╗"] if border else []
        grid = self.grid
        if(reverse):
            grid = reversed(grid)
        for row in grid:
            line = "║" if border else ""
            for cell in row:
                line += str(cell)
            line += "║" if border else ""
            res.append(line)
        if border:
            res.append("╚" + ('═' * self.width) + "╝")
        return res

    def __str__(self):
        return "\n"+"\n".join(self.build_str(self, border = True))

    def get_cell(self, row, col):
        return self.grid[row][col]
