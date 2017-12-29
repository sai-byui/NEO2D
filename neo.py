from enum import Enum

import _thread
import pygame

from neo_body.ears import Ears
from neo_body.eyes import Eyes
from neo_body.hands import Hands
from neo_body.memory import Memory
from neo_body.mouth import Mouth
from neo_body.legs import Legs
from neo_body.wernicke_area import Wernicke_Area

from bot import Bot
from raycast import RayCaster
from pathfinder import Pathfinder

from agent import Agent


RECTANGLE_STARTING_X = 550
RECTANGLE_STARTING_Y = 200
MARGIN = 48

RED = (255, 0, 0)


class NEO(Agent):
    """Controls the behaviors of the NEO bot

    NEO's decisions are based on its current_behavior state. The state is determined by the conditions of its
    environment. A full list of behaviors can be found at the bottom of this module in the
    PilotAgentBehavior class."""

    def __init__(self, environment=None):
        """sets up details about the red rectangle as well as variables for A.I. behavior"""
        super(NEO, self).__init__("neo", environment)

        # the bot object represents NEO's physical body
        # it performs the tasks as directed by the body part classes below
        self.bot = Bot()
        # set the bot's image and angle
        self.bot.image = pygame.Surface([16, 16])
        self.bot.image = pygame.transform.scale(pygame.image.load('Neo.png'), (25, 25))
        self.original_image = self.bot.image.copy()
        self.angle = 90
        # set the starting position
        self.bot.rect.x = RECTANGLE_STARTING_X
        self.bot.rect.y = RECTANGLE_STARTING_Y
        # place the coordinates of our rectangle in a tuple to update the game manager
        self.red_coordinate = (self.bot.rect.x, self.bot.rect.y)
        self.rect = self.bot.rect

        # these different body part classes help modularize the various functions NEO performs
        self.eyes = Eyes()
        self.hands = Hands()
        self.legs = Legs()
        self.memory = Memory()
        self.mouth = Mouth()
        # self.ears = Ears()
        self.wernicke_area = Wernicke_Area()

        # these coordinates tell the agent how far away the object is
        self.object_coordinates = None
        self.distance_from_object = 0
        self.current_position = 0

        self.path_course = []
        self.path_found = False
        self.next_node_coordinates = None

        # variables for A.I. behavior
        self.inspecting = False
        self.detected_objects = pygame.sprite.Group()

        self.current_behavior = BEHAVIOR_STATE.SCANNING
        self.pathfinder = Pathfinder()

    def act_out_decision(self):
        pass

    def check_distance_from_object(self):
        self.update_coordinates()
        self.distance_from_object = \
            abs(self.object_coordinates[0] - self.red_coordinate[0]) + abs(self.object_coordinates[1] - self.red_coordinate[1])

    def determine_behavior(self):
        if not self.detected_objects:
            self.current_behavior = BEHAVIOR_STATE.SCANNING
        elif self.inspecting:
            self.current_behavior = BEHAVIOR_STATE.INSPECTING
        elif self.detected_objects and not self.path_found:
            self.current_behavior = BEHAVIOR_STATE.PATH_FINDING
        elif self.path_found:
            self.current_behavior = BEHAVIOR_STATE.APPROACHING


    def determine_object_position(self):
        """"used to determine which direction the red player should turn to face object"""
        if self.red_coordinate[0] + MARGIN >= self.object_coordinates[0] >= MARGIN - self.red_coordinate[0]:
            # red player is above blue player
            if self.red_coordinate[1] < self.object_coordinates[1] - MARGIN:
                self.current_position = PilotCurrentPosition.ABOVE

            # red player is below blue player
            elif self.red_coordinate[1] > self.object_coordinates[1] + MARGIN:
                self.current_position = PilotCurrentPosition.BELOW
            # red player is right of blue
            elif self.red_coordinate[0] > self.object_coordinates[0]:
                self.current_position = PilotCurrentPosition.RIGHT
            # red player is left of blue
            elif self.red_coordinate[0] < self.object_coordinates[0]:
                self.current_position = PilotCurrentPosition.LEFT

    def find_next_node(self):
        """finds the closest node in our path and removes nodes once they are reached"""
        if not (1 <= abs(self.rect.centerx - self.next_node_coordinates[0]) or 1 <= abs(
                    self.rect.centery - self.next_node_coordinates[1])):
            self.path_course.pop(0)
            if self.path_course:
                self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)

    def is_healthy(self):
        return self.hit_points > 50

    def make_decision(self):
        self.determine_behavior()
        if self.current_behavior == BEHAVIOR_STATE.SCANNING:
            self.legs.rotate()
            self.angle = self.ask("legs", "angle")
            self.eyes.scan_room()
            _thread.start_new_thread(self.mouth.speak, ("Scanning Room",))
        elif self.current_behavior == BEHAVIOR_STATE.PATH_FINDING:
            self.path_course = self.pathfinder.find_path(self.object_coordinates)
            self.path_found = True
            self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)
        elif self.current_behavior == BEHAVIOR_STATE.APPROACHING:
            if not self.path_course:
                self.path_found = False
                self.inspecting = True
                return
            self.find_next_node()
            self.move_to_next_node()
        elif self.current_behavior == BEHAVIOR_STATE.INSPECTING:
            if not self.mouth.inspection_message_spoken:
                self.mouth.stopSentence()
                _thread.start_new_thread(self.mouth.speak, ("Inspecting Object",))
                self.mouth.inspection_message_spoken = True
            pass


    def move_to_next_node(self):
        """tells the bot which direction to move to reach the next node in its path"""
        if self.next_node_coordinates[0] < self.rect.centerx:
            self.bot.move(-2, 0)
        elif self.next_node_coordinates[0] > self.rect.centerx:
            self.bot.move(2, 0)

        # up and down
        if self.next_node_coordinates[1] < self.rect.centery:
            self.bot.move(0, -2)
        elif self.next_node_coordinates[1] > self.rect.centery:
            self.bot.move(0, 2)

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




    def setup_bot_map(self):
        self.bot.wall_list = self.environment.get_object("wall_list")

    def shoot(self):
        if self.bot.reloaded():
            bullet_list = self.environment.get_object("bullet_list")
            if self.current_position == PilotCurrentPosition.LEFT:
                bullet_list.add(self.bot.shoot_right())
            elif self.current_position == PilotCurrentPosition.RIGHT:
                bullet_list.add(self.bot.shoot_left())
            elif self.current_position == PilotCurrentPosition.ABOVE:
                bullet_list.add(self.bot.shoot_down())
            elif self.current_position == PilotCurrentPosition.BELOW:
                bullet_list.add(self.bot.shoot_up())

    def update_coordinates(self):
        self.red_coordinate = (self.rect.x, self.rect.y)
        self.object_coordinates = self.ask("blue_player_pilot", "blue_coordinate")


class PilotAgentBehavior(Enum):
    FINDING_PATH = 0
    CHASING = 1
    SHOOTING = 2
    FLEEING = 4
    HIDING = 8


class PilotCurrentPosition(Enum):
    ABOVE = 1
    BELOW = 2
    LEFT = 3
    RIGHT = 4

class BEHAVIOR_STATE(Enum):
    SCANNING = 1
    APPROACHING = 2
    INSPECTING = 3
    FINISHED = 4
    PATH_FINDING = 5