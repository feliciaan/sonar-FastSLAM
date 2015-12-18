SIZE = 100  # Amount of cells
CELL_SIZE = 5  # In cm


class OccupancyGridMap:
    def __init__(self, width=SIZE, height=SIZE):
        self.width = width
        self.height = height
        self.grid = [[Cell() for _ in range(height)] for _ in range(width)]

    def __iter__(self):
        return iter(self.grid)

    def distance_to_closest_object_in_cone(self, pose, cone_width_angle):
        # TODO: plz implement me
        pass

    def get_cone(self, pose, cone_angle, radius):
        # TODO: plz implement me
        pass


class Cone:
    def __init__(self, edge, inside):
        # Iterable of cells on edge of the cone
        self.edge = edge
        # Iterable of cells inside the cone
        self.inside = inside


class Cell:
    def __init__(self):
        """
        self.occupied is a log-odds value (from -inf to inf), where
           0 means unknown,
           -inf means certainly free,
           and inf means certainly occupied.
        """
        self.occupied = 0
