import pygame
from Grid import Grid


class Rock:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = Grid(grid, None)
        self.rect = None

    def update(self, center_pos, size):
            if self.rect is None:
                center_pos = (center_pos[0] - size[0] / 2 + 5, center_pos[1] - size[1] / 2 + 5)
                size = (size[0] - 10, size[1] -10)
                self.rect = pygame.Rect(center_pos, size)
            pygame.draw.rect(self.screen, "black", self.rect)
            return True