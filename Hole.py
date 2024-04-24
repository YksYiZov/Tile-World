import time
import random

import pygame
from Grid import Grid
from Setting import *


class Hole:
    def __init__(self, screen, grid, life, score):
        self.screen = screen
        self.grid = Grid(grid, None)
        self.life_cycle = random.randint(life[0], life[1])
        self.birth = 0
        self.score = random.randint(score[0], score[1])
        self.rect = None

    def update(self, center_pos, size):
        if self.life_cycle < self.birth:
            return False
        else:
            if self.rect is None:
                center_pos = (center_pos[0] - size[0] / 2 + 5, center_pos[1] - size[1] / 2 + 5)
                size = (size[0] - 10, size[1] -10)
                self.rect = pygame.Rect(center_pos, size)
            self.birth += 1
            pygame.draw.rect(self.screen, "blue", self.rect)
            return True