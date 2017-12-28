import os

import pygame
from agent import Agent
from game_manager import GameManager


class MainManager(Agent):
    """The main driver class of the program and the top of the manager hierarchy"""

    def __init__(self):
        """default constructor"""
        super(MainManager, self).__init__("main_manager")
        self.game_manager = GameManager()
        self.clock = None

    def initialize_pygame(self):
        """sets up the pygame variables for running the game"""
        # initialize pygame
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()

        # clock to keep track of frame rate
        self.clock = pygame.time.Clock()

    def manage_bot_arena(self):
        """calls the game_manager to set up variables and then initializes the game loop"""
        self.initialize_pygame()
        self.game_manager.build_environment()
        self.game_manager.initialize_screen()
        self.game_manager.setup_players()

        while self.game_manager.running_game:
            self.clock.tick(60)
            self.game_manager.run_game()

# the code that actually runs the program
main_manager = MainManager()
main_manager.manage_bot_arena()


