from agent import Agent
import pygame

NEO_STARTING_X = 550
NEO_STARTING_Y = 200

class Legs(Agent):
    """Allows NEO to move in its environment"""

    def __init__(self):
        """default constructor"""
        super(Legs, self).__init__("legs")
        self.bot = self.share("neo", "bot")
        self.angle = self.ask("neo", "angle")
        self.original_image = self.share("neo", "original_image")
        self.x_pos = NEO_STARTING_X
        self.y_pos = NEO_STARTING_Y

    def rotate(self):
        self.angle += 1
        # key = pygame.key.get_pressed()
        # if key[pygame.K_LEFT]:
            # self.angle += 4
        # if key[pygame.K_RIGHT]:
            # self.angle -= 4
        # self.angle += 2
        self.angle %= 360
        self.bot.angle_facing = self.angle
        self.bot.update_dx_dy()

        rect_center = self.bot.image.get_rect()
        self.bot.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        rot_rect = rect_center.copy()
        rot_rect.center = self.bot.image.get_rect().center
        self.bot.image = self.bot.image.subsurface(rot_rect).copy()

    def walk(self, dx, dy):
        self.bot.move(dx, dy)
        self.x_pos = self.bot.rect.x
        self.y_pos = self.bot.rect.y
        # print("dx:{} dy:{}".format(self.x_pos, self.y_pos))
