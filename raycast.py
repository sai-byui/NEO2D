import pygame
import math

RED = (255, 0, 0)
RAYCAST_LENGTH = 20
RAYCAST_WIDTH = 2
RAYCAST_SPEED = 5


class RayCaster(pygame.sprite.Sprite):
    def __init__(self, positionX, positionY, dx, dy, angle):
        # Call the parent class (Sprite) constructor
        super(RayCaster, self).__init__()
        if 1 <= divmod(angle, 45)[0] < 3 or 5 <= divmod(angle, 45)[0] < 7:
            self.image = pygame.Surface([RAYCAST_LENGTH, RAYCAST_WIDTH], pygame.SRCALPHA, 32)
            self.rect = pygame.Rect(0, 0, RAYCAST_LENGTH, RAYCAST_WIDTH)
        else:
            self.image = pygame.Surface([RAYCAST_WIDTH, RAYCAST_LENGTH], pygame.SRCALPHA, 32)
            self.rect = pygame.Rect(0, 0, RAYCAST_WIDTH, RAYCAST_LENGTH)
        # this line makes the raycast object visible
        self.image.fill(RED)
        self.dx = dx
        self.dy = dy
        self.rect.centerx = positionX + dx
        self.rect.centery = positionY + dy


    def update_movement(self):
        self.rect.x += self.dx * RAYCAST_SPEED
        self.rect.y += self.dy * RAYCAST_SPEED

    def rotate_point(self, pivot_x, pivot_y, angle, p):
        pass

