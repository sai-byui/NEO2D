import pygame
import math

RED = (255, 0, 0)


class RayCaster(pygame.sprite.Sprite):
    def __init__(self, positionX, positionY, dx, dy, angle):
        # Call the parent class (Sprite) constructor
        super(RayCaster, self).__init__()
        if 1 <= divmod(angle, 45)[0] < 3 or 5 <= divmod(angle, 45)[0] < 7:
            self.image = pygame.Surface([100, 2], pygame.SRCALPHA, 32)
            self.rect = pygame.Rect(0, 0, 100, 2)
        else:
            self.image = pygame.Surface([2, 100], pygame.SRCALPHA, 32)
            self.rect = pygame.Rect(0, 0, 2, 100)
        # this line makes the raycast object visible
        self.image.fill(RED)
        self.dx = dx
        self.dy = dy
        self.rect.centerx = positionX + dx * 2
        self.rect.centery = positionY + dy * 2


    def update_movement(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def rotate_point(self, pivot_x, pivot_y, angle, p):
        pass

