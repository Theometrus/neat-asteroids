import math


class Grid:
    def __init__(self, width, height, block_size):
        self.grid = {}
        for i in range(-2 * block_size, width + 2 * block_size, block_size):
            for j in range(-2 * block_size, height + 2 * block_size, block_size):
                self.grid[(i, j)] = []

        self.block_size = block_size
        self.width = width
        self.height = height

    def get_key(self, x, y):
        idx_x = math.floor(x / self.block_size)
        idx_y = math.floor(y / self.block_size)
        key_x = idx_x * self.block_size
        key_y = idx_y * self.block_size

        return key_x, key_y

    def insert(self, elem, x, y):
        self.grid[self.get_key(x, y)].append(elem)

    def delete(self, elem, x, y):
        try:
            self.grid[self.get_key(x, y)].remove(elem)
        except ValueError:
            pass

    def get_zone(self, x, y):
        return self.grid[self.get_key(x, y)]
