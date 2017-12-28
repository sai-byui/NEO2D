from agent import Agent
import pygame


class Legs(Agent):
    """Allows NEO to move in its environment"""

    def __init__(self):
        """default constructor"""
        super(Legs, self).__init__("legs")
        self.bot = self.share("neo", "bot")
        self.angle = self.ask("neo", "angle")
        self.original_image = self.share("neo", "original_image")
        # self.position = self.ask("neo", "position")

    def rotate(self):
        self.angle += .5
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.angle += 4
        if key[pygame.K_RIGHT]:
            self.angle -= 4
        # self.angle += 2
        self.angle %= 360
        self.bot.angle_facing = self.angle
        self.bot.update_dx_dy()

        rect_center = self.bot.image.get_rect()
        self.bot.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        rot_rect = rect_center.copy()
        rot_rect.center = self.bot.image.get_rect().center
        self.bot.image = self.bot.image.subsurface(rot_rect).copy()

    def walk(self):
        pass
