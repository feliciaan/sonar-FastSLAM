
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
        self.blocksize = blocksize
        self.cellsize = cellsize
        self.cellsPerSmaller = int(blocksize / cellsize)
        self.smallmaps = dict()
        self.xrange = (0,0)
        self.yrange = (0,0)
        init_kwadrants  = [(0,0)]
        for kwadrant in init_kwadrants:
            self.smallmaps[kwadrant] = SimpleOccupancyGridMap(self.cellsPerSmaller, self.cellsPerSmaller)

    """
    Gets the cell at x, y
    Might initialize new blocks if needed, so don't ask things unless needed
    """
    def getCell(self, x, y):
        # get smaller map
        xi = int( x // self.blocksize)
        yi = int( y // self.blocksize)
        if (xi, yi) not in self.smallmaps:
            self.smallmaps[(xi,yi)] = SimpleOccupancyGridMap(self.cellsPerSmaller, self.cellsPerSmaller)
            (xmin, xmax)    = self.xrange
            self.xrange     = (min(xmin, xi), max(xmax, xi) )
            (ymin, ymax)    = self.yrange
            self.yrange     = (min(ymin, yi), max(ymax, yi) )

        smallmap = self.smallmaps[(xi,yi)]

        # get the coordinates in the smaller map
        xd  = x % self.blocksize
        yd  = y % self.blocksize
        xd  = int( xd // self.cellsize)
        yd  = int( yd // self.cellsize)
        row = yd
        col = xd
        return smallmap.getCell(row,col)

    def build_str(self, border=False):
        (ymin, ymax)    = self.yrange
        (xmin, xmax)    = self.xrange
        result  = ""
        cellsPerSmaller = self.cellsPerSmaller + (2 if border else 0)
        emptyRepr   = ["." * cellsPerSmaller] * cellsPerSmaller
        for y in range(ymax, ymin-1, -1):
            lines = [""] * (cellsPerSmaller)
            for x in range(xmin, xmax+1):
                reprs   = emptyRepr
                if (x,y) in self.smallmaps:
                    reprs = self.smallmaps[(x,y)].build_str(reverse=True, border = border, borderMsg = str((x,y)))
                    if (x,y) == (0,0):
                        orig_repr   = self.getCell(0,0).origin_str();
                        reprs[-1] = orig_repr + reprs[-1][1:]

                for i in range(0, cellsPerSmaller):
                    lines[i] = lines[i] + reprs[i]
            result += "\n" + "\n".join(lines)

        return ("GridMap with blocksize "+str(self.blocksize)+"cm and resolution "+str(self.cellsize)+"cm:\n"+ result)


    def __str__(self):
        return self.build_str()


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

    def getCell(self, row, col):
        return self.grid[row][col]


class Cell:
    def __init__(self, occupation=None):
        """self.occupied is a value between 0 (free) and 100 (occupied) if it's occupancy is known, else
        None.
        It's percentage indicates how sure we are about something is there.
        """
        self.occupation = occupation
        self.hasRobot = False

    def set(self, occupation):
        if(occupation is None):
            self.occupation = None
            return
        if(isinstance(occupation, bool)):
            occupation = 1 if occupation else 0

        assert (0 <= occupation <= 1), "Invalid occupation range, expected value between 0 and 100"
        self.occupation = occupation



    def get(self):
        return self.occupation

    def occupied():
        return self.occupation >= 0.5


    def __str__(self):
        if self.hasRobot:
            return self.hasRobot
        if self.occupation is None:
           return '░'
        chars = " ▁▂▃▄▅▆▇█"
        i = int(self.occupation * (len(chars)-1))
        return chars[i]
        return str(self.occupation)

    def origin_str(self):
        if self.hasRobot:
            return self.hasRobot
        if self.occupation is None:
            return '◌'
        chars = "○◎◍◒◕●◙"
        i = int(self.occupation * (len(chars)-1))
        return chars[i]
        return str(self.occupation)


    def __repr__(self):
        if (self.occupation is None):
            return "Cell()"

        return "Cell("+repr(self.occupation)+")"
