import math
import random
import time

import pygame
from Grid import Grid
from Setting import *

class Agent:
    def __init__(self, screen, world_size, think_time=1, think_step=math.inf, sk=0):
        self.grid = Grid((0, 0), None)
        self.rect = None
        self.screen = screen
        self.world_size = world_size
        self.action = []
        self.act_count = 0
        self.think_count = 0
        self.think_time = think_time
        self.think_step = think_step
        self.sk = sk
        self.target = None

    def update(self, center_pos, size):
        center_pos = (center_pos[0] - size[0] / 2 + 5, center_pos[1] - size[1] / 2 + 5)
        size = (size[0] - 10, size[1] - 10)
        self.rect = pygame.Rect(center_pos, size)
        pygame.draw.rect(self.screen, "red", self.rect)
        return True

    def find_way(self, holes, rocks):
        hole_grid = [hole.grid for hole in holes]
        now_list = [self.grid]
        passed_list = [rock.grid for rock in rocks]
        while len(list(set(hole_grid).intersection(now_list))) == 0 and len(now_list) != 0:
            new_list = []
            for now in now_list:
                if now not in passed_list:
                    sub_res = self.bfs(now, passed_list, new_list)
                    passed_list = list(set(passed_list).union([now]))
                    if len(sub_res) != 0:
                        new_list = list(set(new_list).union(sub_res))
            passed_list = list(set(passed_list).union(now_list))
            now_list = new_list
        goal = list(set(hole_grid).intersection(now_list))

        if len(goal) == 0:
            return None
        else:
            goal = random.choice(goal)
            if self.target is None:
                self.target = goal
            if goal == self.grid:
                pass
            while goal is not None and goal != self.grid:
                self.action.append(goal)
                goal = goal.father
        return None

    def bfs(self, now, passed_list, new_list):
        next = [Grid((now[0], now[1] - 1 if now[1] - 1 >= 0 else 0), now),
                Grid((now[0], now[1] + 1 if now[1] + 1 < self.world_size[0] else self.world_size[0] - 1), now),
                Grid((now[0] - 1 if now[0] - 1 >= 0 else 0, now[1]), now),
                Grid((now[0] + 1 if now[0] + 1 < self.world_size[1] else self.world_size[1] - 1, now[1]), now)]
        return list(set(next).difference(passed_list).difference(new_list))

    def run(self):
        self.grid = self.action.pop()
        self.grid.father = None
        if len(self.action) == 0:
            self.target = None
            return self.grid
        else:
            return None

    def act(self, holes, rocks, new_hole):
        if self.act_count >= self.think_step \
                or len(self.action) == 0 \
                or (self.target_dis(holes) and self.sk == 1)\
                or ((self.target_dis(holes) or self.nearer_hole(holes)) and self.sk == 2)\
                or ((self.target_dis(holes) or new_hole) and self.sk == 3):
            self.action = []
            self.act_count = 0
            if self.think_count >= self.think_time:
                self.find_way(holes, rocks)
                self.think_count = 0
            else:
                self.think_count += 1
            return None
        else:
            self.act_count += 1
            return self.run()

    def target_dis(self, holes):
        grid_holes = [hole.grid for hole in holes]
        if self.target is not None and self.target not in grid_holes:
            self.target = None
            return True
        else:
            return False

    def nearer_hole(self, holes):
        grid_holes = [hole.grid for hole in holes]
        if self.target is None:
            return False
        min_dist = math.dist(self.target, self.grid)
        for grid_hole in grid_holes:
            if min_dist > math.dist(self.grid, grid_hole):
                self.target = None
                return True
        return False