SIZE = 100  # Amount of cells
CELL_SIZE = 5  # In cm


class OccupancyGridMap:
    def __init__(self, width=SIZE, height=SIZE):
        self.width = width
        self.height = height
        self.grid = [[Cell() for _ in range(height)] for _ in range(width)]

    def __iter__(self):
        return iter(self.grid)


class Cell:
    def __init__(self):
        """self.occupied is True or False if it's occupancy is known, else
        None."""
        self.occupied = None
