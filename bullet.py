from enum import Enum

import pygame
green = (0, 255, 0)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, direction):
        # Call the parent class (Sprite) constructor
        super(Bullet, self).__init__()
        # for shooting directions: 1 = UP, 2 = DOWN, 3 = LEFT, 4 = RIGHT
        self.direction = direction
        if self.direction == 1 or self.direction == 2:
            self.image = pygame.Surface([2, 6])
            self.rect = pygame.Rect(0, 0, 2, 6)
        else:
            self.image = pygame.Surface([6, 2])
            self.rect = pygame.Rect(0, 0, 6, 2)

        self.image.fill(green)

    def move_up(self):
        self.rect.y -= 8

    def move_down(self):
        self.rect.y += 8

    def move_left(self):
        self.rect.x -= 8

    def move_right(self):
        self.rect.x += 8

    def update_movement(self):
        """moves the bullet's position based on its direction"""
        movement = {1: self.move_up, 2: self.move_down, 3: self.move_left, 4: self.move_right}
        movement[self.direction]()


class BulletDirection(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
