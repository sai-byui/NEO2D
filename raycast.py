import pygame
import math

RED = (255, 0, 0)
RAYCAST_LENGTH = 20
RAYCAST_WIDTH = 2
RAYCAST_SPEED = 5


class RayCaster(pygame.sprite.Sprite):
    """sensors that neo uses to scan objects in its area. It performs similar to the bullet class
        if the ray caster collides with an object neo is notified"""
    def __init__(self, positionX, positionY, dx, dy, angle):
        # Call the parent class (Sprite) constructor
        # the ray changes shape based on the angle it is traveling
        super(RayCaster, self).__init__()
        self.image = pygame.Surface([RAYCAST_LENGTH, RAYCAST_WIDTH], pygame.SRCALPHA, 32)
        self.rect = pygame.Rect(0, 0, RAYCAST_LENGTH, RAYCAST_WIDTH)
        # this line makes the raycast object visible
        self.image.fill(RED)
        # these specify what direction the ray cast is traveling
        self.dx = dx
        self.dy = dy
        self.rect.centerx = positionX + dx
        self.rect.centery = positionY + dy
        self.image = pygame.transform.rotate(self.image, angle)


    def update_movement(self):
        self.rect.x += self.dx * RAYCAST_SPEED
        self.rect.y += self.dy * RAYCAST_SPEED

    def rotate_point(self, pivot_x, pivot_y, angle, p):
        pass

