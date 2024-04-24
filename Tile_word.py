import pygame

from Agent import Agent
from Rock import Rock
from Setting import *

class Tile_word:
    def __init__(self, world_size, margin, screen, line_color=(0, 0, 0)):
        self.world_size = world_size
        self.margin = margin
        self.screen = screen
        self.line_color = line_color
        self.container = [[None for i in range(world_size[0])] for j in range(world_size[1])]
        self.holes = []
        self.rocks = []
        self.total_score = 0
        self.get_score = 0
        self.grid2pos = None
        self.pos2grid = None
        self.grid_size = None

    def draw_lines(self):
        width = self.screen.get_width()
        height = self.screen.get_height()

        grid_width = (width - 2 * self.margin) / self.world_size[0]
        grid_height = (height - 2 * self.margin) / self.world_size[1]

        if self.grid_size is None:
            self.grid_size = (grid_width, grid_height)

        h_lines = [[(self.margin, self.margin + grid_height * i), (width - self.margin, self.margin + grid_height * i)]
                   for i in range(self.world_size[0] + 1)]
        v_lines = [[(self.margin + grid_width * i, self.margin), (self.margin + grid_width * i, height - self.margin)]
                   for i in range(self.world_size[1] + 1)]

        for i, j in zip(h_lines, v_lines):
            pygame.draw.line(self.screen, self.line_color, i[0], i[1])
            pygame.draw.line(self.screen, self.line_color, j[0], j[1])

        def tuple2pos(grid):
            return self.margin + grid.grid[0] * grid_width + grid_width / 2, self.margin + grid.grid[1] * grid_height + grid_height / 2

        def pos2tuple(pos):
            return (pos[0] - self.margin) // width, (pos[1] - self.margin) // height

        self.grid2pos = tuple2pos
        self.pos2grid = pos2tuple

    def draw_obj(self):
        for i in range(len(self.container)):
            for j in range(len(self.container[i])):
                if self.container[i][j] is not None:
                    if not self.container[i][j].update(self.grid2pos(self.container[i][j].grid), self.grid_size):
                        self.holes.remove(self.container[i][j])
                        self.container[i][j] = None
                    else:
                        self.change_place(i, j)


    def update(self):
        self.draw_lines()
        self.draw_obj()

    def check(self, grid):
        if self.container[grid[0]][grid[1]] is None:
            return True
        else:
            return False


    def add(self, obj, grid, type):
        self.container[grid[0]][grid[1]] = obj
        if type == HOLE:
            self.holes.append(obj)
            self.total_score += obj.score
        elif type == ROCK:
            self.rocks.append(obj)
        elif type == AGENT:
            pass
        else:
            print(obj, "未知类别")

    def destroy(self, grid):
        if grid is not None:
            if self.container[grid[0]][grid[1]] in self.holes:
                self.get_score += self.container[grid[0]][grid[1]].score
                self.holes.remove(self.container[grid[0]][grid[1]])
                self.container[grid[0]][grid[1]] = None
            else:
                if self.container[grid[0]][grid[1]] is not None:
                    print("摧毁失败，位置在", grid)

    def change_place(self, i, j):
        if isinstance(self.container[i][j], Agent):
            grid = self.container[i][j].grid
            if (i, j) != grid.grid and self.container[grid[0]][grid[1]] is None:
                self.container[grid[0]][grid[1]] = self.container[i][j]
                self.container[i][j] = None
