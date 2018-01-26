import _thread
import threading

import pygame
from agent import Agent
from blue_player_pilot import BluePlayerPilot
from environment import Environment
from map_builder import MapBuilder
from neo import NEO

# event values for handling during game play
SHOOTING = pygame.USEREVENT + 1


class GameManager(Agent):
    """The game_manager handles all agents responsible for making the game run"""

    def __init__(self):
        """sets up the game variables and then initializes its employee agents"""
        super(GameManager, self).__init__("game_manager")
        self.house = Environment()

        self.screen = None
        # screen size
        self.screen_height = 444
        self.screen_width = 1116
        self.running_game = True

        # player list
        self.player_list = pygame.sprite.Group()
        self.house.add_object("player_list", self.player_list)
        # holds bullet list
        self.bullet_list = pygame.sprite.Group()
        self.house.add_object("bullet_list", self.bullet_list)
        # holds the sprites that make up the wall
        self.wall_list = pygame.sprite.Group()
        self.house.add_object("wall_list", self.wall_list)
        # holds the objects that are placed in the environment for Neo to interact with
        self.object_list = pygame.sprite.Group()
        self.house.add_object("object_list", self.object_list)
        # this holds the awesome laser beams that Neo shoots from his face
        self.raycast_list = pygame.sprite.Group()
        self.house.add_object("raycast_list", self.raycast_list)

        # initialize agents and place them in the environment
        self.map_builder = MapBuilder(self.house)
        self.neo = NEO(self.house)
        self.blue_player_pilot = BluePlayerPilot(self.house)

    def build_environment(self):
        """calls the map builder agent to parse through the level file and create the map of the game"""
        self.map_builder.build_arena()
        self.map_builder.insert_objects()
        self.wall_list = self.house.get_object("wall_list")
        self.object_list = self.house.get_object("object_list")


    def check_bullet_collisions(self):
        """checks if any bullets have collided with objects and need to be removed"""
        for bullet in self.bullet_list:
            bullet.update_movement()
            self.check_if_bullet_is_in_boundaries(bullet)
            self.check_player_bullet_collision(bullet)
            self.check_wall_bullet_collision(bullet)
            self.check_object_ray_collision(bullet)

    def check_if_bullet_is_in_boundaries(self, bullet):
        """removes the bullet if it is no longer on the map"""
        if bullet.rect.x < 0 or bullet.rect.x > 1116 or bullet.rect.y < 0 or bullet.rect.y > 444:
            self.bullet_list.remove(bullet)

    def check_player_bullet_collision(self, bullet):
        """checks if the bullet has collided with a player"""
        # for player in self.player_list:
        #     if bullet.rect.colliderect(player):
        #         player.hit_points -= 10
        #         self.bullet_list.remove(bullet)
        pass


    def check_object_ray_collision(self, bullet):
        for object in self.object_list:
            if bullet.rect.colliderect(object):
                # self.neo.mouth.stopSentence()
                sentence = object.name + " detected"
                # _thread.start_new_thread(self.neo.mouth.identify_detected_object, (sentence,))
                self.neo.object_coordinates = (object.rect.x, object.rect.y)
                self.neo.detected_objects.add(object)
                self.bullet_list.remove(bullet)

    def check_wall_bullet_collision(self, bullet):
        for wall_block in self.wall_list:
            if bullet.rect.colliderect(wall_block):
                self.bullet_list.remove(bullet)


    def check_pygame_events(self):
        """checks any for events such as keys pressed or A.I. actions that change the state of the game"""
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running_game = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.running_game = False

    def draw(self):
        """displays the game images on the screen"""
        self.screen.fill((0, 0, 0))
        self.object_list.draw(self.screen)
        self.player_list.draw(self.screen)
        self.wall_list.draw(self.screen)
        self.bullet_list.draw(self.screen)
        pygame.display.flip()

    def initialize_screen(self):
        # Set up the display
        pygame.display.set_caption("BOT ARENA 3.0!")
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def run_game(self):
        """calls the player agent's to perform their moves and check's for bullet movement"""
        self.check_pygame_events()
        self.neo.make_decision()
        self.blue_player_pilot.check_input_for_actions()
        self.check_bullet_collisions()
        self.draw()

    def setup_players(self):
        """adds the player sprites to the list of players for reference and sets up the bots in their environment"""
        self.player_list.add(self.neo.bot, self.blue_player_pilot.bot)
        self.blue_player_pilot.setup_bot_map()
        self.neo.setup_bot_map()




