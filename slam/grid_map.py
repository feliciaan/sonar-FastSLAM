SIZE = 100  # Amount of cells
CELL_SIZE = 5  # In cm


class OccupancyGridMap:
    def __init__(self, width=SIZE, height=SIZE):
        self.width = width
        self.height = height
        """
        Grid[ROW][HEIGHT]
        """
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]

    def __iter__(self):
        return iter(self.grid)


    def __str__(self):
        res = "╔" + ('═' * self.width) + "╗\n║"
        for row in self.grid:
            for cell in row:
                res += str(cell)
            res += "║\n║"
        res = res[:-1] + "╚" + ('═' * self.width) + "╝"
        return res

    def set(self, row, col, occupation):
        self.grid[row][col].set(occupation)

    def get(self, row, col):
        return self.grid[row][col].get()

    def occupied(self, row, col):
        return self.grid[row][col].occupied()


class Cell:
    def __init__(self, occupation=None):
        """self.occupied is a value between 0 (free) and 100 (occupied) if it's occupancy is known, else
        None.
        It's percentage indicates how sure we are about something is there.
        """
        self.occupation = occupation

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
        if self.occupation is None:
            return '░'
        chars = " -~+=%#█" # " ▁▂▃▄▅▆▇█"
        i = int(self.occupation * (len(chars)-1))
        return chars[i]


    def __repr__(self):
        if (self.occupation is None):
            return "Cell()"

        return "Cell("+repr(self.occupation)+")"



grid = OccupancyGridMap(30,10)
print(grid)
for i in range(0,10):
    grid.set(3,2+i, i/10)
    grid.set(3,21-i, i/10)

print(grid)
