class Grid:
    def __init__(self, grid, father):
        self.grid = grid
        self.father = father

    def __eq__(self, other):
        if self.grid == other.grid:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.grid)

    def __str__(self):
        return str(self.grid)

    def __getitem__(self, item):
        return self.grid[item]