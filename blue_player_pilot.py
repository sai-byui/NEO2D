import pygame
from agent import Agent
from bot import Bot
from bullet import *

RECTANGLE_STARTING_X = 64
RECTANGLE_STARTING_Y = 64

BLUE = (0, 0, 255)


class BluePlayerPilot(Agent):
    """the blue rectangle agent whose decisions are determined by the user"""

    def __init__(self, environment=None):
        super(BluePlayerPilot, self).__init__("blue_player_pilot", environment)

        self.bot = Bot()
        self.bot.image.fill(BLUE)
        self.bot.rect.x = RECTANGLE_STARTING_X
        self.bot.rect.y = RECTANGLE_STARTING_Y

        self.rect = self.bot.rect
        self.blue_coordinate = (self.rect.x, self.rect.y)
        self.dx = 0
        self.dy = 0
        self.angle = 0

    def check_input_for_actions(self):
        """checks user input in order to make decisions"""
        # self.make_movements()
        # self.rotate()
        self.shoot()
        self.update_position()

    def make_movements(self):
        """checks for any movements keys being pressed and moves accordingly"""
        self.dx = 0
        self.dy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.dx = -2
        if key[pygame.K_RIGHT]:
            self.dx = 2
        if key[pygame.K_UP]:
            self.dy = -2
        if key[pygame.K_DOWN]:
            self.dy = 2

        self.bot.move(self.dx, self.dy)




    def shoot(self):
        """adds bullets to the game"""
        # first determine if we can shoot
        if self.bot.reloaded():
            # get the bullet list from the environment
            bullet_list = self.environment.get_object("bullet_list")
            key = pygame.key.get_pressed()
            if key[pygame.K_a]:
                bullet_list.add(self.bot.shoot_left())
            elif key[pygame.K_d]:
                bullet_list.add(self.bot.shoot_right())
            elif key[pygame.K_w]:
                bullet_list.add(self.bot.shoot_up())
            elif key[pygame.K_s]:
                bullet_list.add(self.bot.shoot_down())

    def setup_bot_map(self):
        """sets the bot wall_list so that wall collision can be detected"""
        self.bot.wall_list = self.environment.get_object("wall_list")

    def update_position(self):
        """updates the player's coordinates for reference by other agents"""
        self.blue_coordinate = (self.rect.x, self.rect.y)

