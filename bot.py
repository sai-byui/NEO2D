import pygame
import math
from bullet import Bullet
from raycast import RayCaster


class Bot(pygame.sprite.Sprite):

    def __init__(self):
        super(Bot, self).__init__()
        self.image = pygame.Surface([16, 16])
        self.rect = pygame.Rect(0, 0, 16, 16)
        self.wall_list = None

        # game variables
        self.score = 0
        self.hit_points = 100
        self.ammo = 100
        # this determines which direction the bot is facing from 0 to 359 degrees
        self.angle_facing = 0
        self.dx = 0
        self.dy = -1

        # time between bullet shots in milliseconds
        self.reload_time = 800
        self.last_shot_time = pygame.time.get_ticks()

    def reloaded(self):
        if self.last_shot_time > pygame.time.get_ticks() - self.reload_time:
            return False
        else:
            return True


    def move(self, dx, dy):
        """takes movement parameters and applies the value to the x and y coordinates"""
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0 or dy != 0:
            self.move_single_axis(dx, dy)

    def move_single_axis(self, dx, dy):
        """checks for collision into walls while moving coordinates"""
        # Move the rect
        self.rect.x += dx
        self.rect.y += dy
        # If you collide with an wall, set the side of the rectangle equal to the wall to give the appearance of
        # collision
        for wall in self.wall_list:
            if self.rect.colliderect(wall.rect):
                if 0 < dx and dx > abs(dy):  # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                    break
                elif dx < 0 and abs(dx) > abs(dy):  # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                    break
                elif dy > 0 and dy > abs(dx):  # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                    break
                elif dy < 0 and abs(dy) > abs(dx):  # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.rect.bottom
                    break

    def scan_ray_center(self):
        self.update_dx_dy()
        raycast = RayCaster((self.rect.centerx + self.dx * 5), (self.rect.centery + self.dy * 5), self.dx, self.dy, self.angle_facing)
        self.last_shot_time = pygame.time.get_ticks()
        return raycast

    def scan_ray_left(self):
        self.update_dx_dy_left()
        raycast = RayCaster((self.rect.left + self.dx * 6), (self.rect.centery + self.dy * 6), self.dx, self.dy, self.angle_facing)
        self.last_shot_time = pygame.time.get_ticks()
        return raycast

    def scan_ray_right(self):
        self.update_dx_dy_right()
        raycast = RayCaster((self.rect.right + self.dx * 6), (self.rect.centery + self.dy * 6), self.dx, self.dy, self.angle_facing)
        self.last_shot_time = pygame.time.get_ticks()
        return raycast


    def shoot_up(self):
            bullet = Bullet(1)
            bullet.rect.x = self.rect.centerx
            bullet.rect.y = self.rect.y - 8
            self.last_shot_time = pygame.time.get_ticks()
            return bullet

    def shoot_down(self):
            bullet = Bullet(2)
            bullet.rect.x = self.rect.centerx
            bullet.rect.y = self.rect.y + 16
            self.last_shot_time = pygame.time.get_ticks()
            return bullet

    def shoot_left(self):
            bullet = Bullet(3)
            bullet.rect.x = self.rect.x - 16
            bullet.rect.y = self.rect.centery
            self.last_shot_time = pygame.time.get_ticks()
            return bullet

    def shoot_right(self):
            bullet = Bullet(4)
            bullet.rect.x = self.rect.x + 16
            bullet.rect.y = self.rect.centery
            self.last_shot_time = pygame.time.get_ticks()
            return bullet

    def update_dx_dy(self):
        self.dx = math.cos(math.radians(self.angle_facing)) * 2
        self.dy = math.sin(math.radians(self.angle_facing)) * -2

    def update_dx_dy_left(self):
        self.dx = math.cos(math.radians(self.angle_facing + 45)) * 2
        self.dy = math.sin(math.radians(self.angle_facing + 45)) * -2

    def update_dx_dy_right(self):
        self.dx = math.cos(math.radians(self.angle_facing - 45)) * 2
        self.dy = math.sin(math.radians(self.angle_facing - 45)) * -2
