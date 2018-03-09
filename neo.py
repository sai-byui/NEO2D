from enum import Enum

import _thread
import pygame

# from neo_body.ears import Ears
from neo_body.eyes import Eyes
from neo_body.hands import Hands
from neo_body.memory import Memory
# from neo_body.mouth import Mouth
from neo_body.legs import Legs
from neo_body.wernicke_area import Wernicke_Area

from bot import Bot
from raycast import RayCaster
from pathfinder import Pathfinder

from agent import Agent


NEO_STARTING_X = 550
NEO_STARTING_Y = 200
MARGIN = 48

RED = (255, 0, 0)


class NEO(Agent):
    """Controls the behaviors of the NEO bot

    NEO has four main tasks:
    1. scan the room for new objects,
    2. approach discovered objects,
    3. inspect objects and gather info about their attributes,
    4. accept queries from the user to test its memory of objects.

    NEO performs these tasks by using the various body part classes located in the neo_body directory. This NEO
    class essentially serves as the 'brain' class and passes commands to all other body parts as needed. NEO and every
    body part class are subclasses of the Agent class, which allows them to safely share info with each other using
    Agent Oriented Programming methods. This allows us to easily add new parts or replace parts altogether."""

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
        self.bot.rect.x = NEO_STARTING_X
        self.bot.rect.y = NEO_STARTING_Y
        # place the coordinates of our rectangle in a tuple to update the game manager
        self.red_coordinate = (self.bot.rect.x, self.bot.rect.y)
        self.rect = self.bot.rect

        # these different body part classes help modularize the various functions NEO performs
        self.eyes = Eyes()
        self.hands = Hands()
        self.legs = Legs()
        self.memory = Memory()
        self.memory.create_object_memory()
        # self.mouth = Mouth()
        # self.ears = Ears()
        self.wernicke_area = Wernicke_Area()

        self.current_object = None

        # these coordinates tell the agent how far away the object is
        self.object_coordinates = None
        self.distance_from_object = 0
        self.current_position = 0

        self.path_course = []
        self.path_found = False
        self.next_node_coordinates = None

        # variables for A.I. behavior
        self.inspecting = False
        self.detected_objects = []
        self.uninspected_objects = []

        self.current_behavior = BEHAVIOR_STATE.SCANNING
        self.pathfinder = Pathfinder()
        self.running_training = True

        #search variables
        self.rotating_counter = 0
        self.location_coordinates = self.ask("memory", "location_coordinates")

        self.sql_statement = None

    def act_out_decision(self):
        pass

    def check_distance_from_object(self):
        self.update_coordinates()
        self.distance_from_object = \
            abs(self.object_coordinates[0] - self.red_coordinate[0]) + \
            abs(self.object_coordinates[1] - self.red_coordinate[1])

    def determine_behavior(self):
        if self.inspecting:
            self.current_behavior = BEHAVIOR_STATE.INSPECTING
        elif self.uninspected_objects and not self.path_found:
            self.current_behavior = BEHAVIOR_STATE.PATH_FINDING
            self.current_object = self.uninspected_objects[0]
        elif self.path_found:
            self.current_behavior = BEHAVIOR_STATE.APPROACHING
        else:
            self.current_behavior = BEHAVIOR_STATE.SCANNING

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

    def filter_detected_objects(self):
        """Decides whether detected objects(currently just 1 at a time) have been inspected before"""
        for obj in self.detected_objects:
            self.sql_statement = "SELECT * FROM objects WHERE object_x_pos = " + str(obj.x) + \
                " AND object_y_pos = " + str(obj.y)
            self.memory.recall_objects()
            if self.ask("memory", "short_term_memory"):
                self.detected_objects.remove(obj)
            else:
                self.uninspected_objects += [obj]
                self.detected_objects.remove(obj)

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
        """Acts out decisions based on the current behavior state"""
        if not self.running_training:
            self.filter_detected_objects()
            self.determine_behavior()
            if self.current_behavior == BEHAVIOR_STATE.SCANNING:
                self.legs.rotate()
                self.angle = self.ask("legs", "angle")
                self.eyes.scan_room()
                # _thread.start_new_thread(self.mouth.speak, ("Scanning Room",))
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
                # if not self.mouth.inspection_message_spoken:
                #     self.mouth.stopSentence()
                #     _thread.start_new_thread(self.mouth.speak, ("Inspecting Object",))
                #     self.mouth.inspection_message_spoken = True
                self.eyes.look_at_object()
                self.hands.pick_up_object()
                self.memory.memorize()
                self.inspecting = False
                self.uninspected_objects.remove(self.current_object)
                self.current_object = None
        else:
            self.run_training()

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

    # def rotate(self): Use the one in legs.py instead
    #     self.angle += .5
    #     key = pygame.key.get_pressed()
    #     if key[pygame.K_LEFT]:
    #         self.angle += 4
    #     if key[pygame.K_RIGHT]:
    #         self.angle -= 4
    #     # self.angle += 2
    #     self.angle %= 360
    #     self.bot.angle_facing = self.angle
    #     self.bot.update_dx_dy()
    #
    #     rect_center = self.bot.image.get_rect()
    #     self.bot.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
    #     rot_rect = rect_center.copy()
    #     rot_rect.center = self.bot.image.get_rect().center
    #     self.bot.image = self.bot.image.subsurface(rot_rect).copy()

    def run_training(self):
        if self.current_behavior != BEHAVIOR_STATE.PATH_FINDING:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.legs.walk(-2, 0)
            if key[pygame.K_RIGHT]:
                self.legs.walk(2, 0)
            if key[pygame.K_UP]:
                self.legs.walk(0, -2)
            if key[pygame.K_DOWN]:
                self.legs.walk(0, 2)

            if key[pygame.K_SPACE]:
                location_name = input("Enter a name for this location:")
                self.memory.save_location(location_name)
            if key[pygame.K_c]:
                command = input("Enter a command to run")
                self.wernicke_area.parse_command(command)
                # location_coordinates = self.ask("wernicke_area", "location_coordinates")
                self.update_coordinates()
                self.current_behavior = self.ask("wernicke_area", "next_behavior")
                self.current_behavior = BEHAVIOR_STATE(7)
                # to do: add division between tasks
                # self.path_course = self.pathfinder.find_path(location_coordinates)
                # self.current_behavior = BEHAVIOR_STATE.PATH_FINDING
                # print(self.path_course)
        elif self.current_behavior == BEHAVIOR_STATE.PATH_FINDING:
            if not self.path_course:
                self.path_found = False
                self.current_behavior = BEHAVIOR_STATE.TRAINING
                return
            else:
                self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)
                self.find_next_node()
                self.move_to_next_node()

    def search_for(self):

        self.legs.rotate()
        self.rotating_counter += 1
        self.angle = self.ask("legs", "angle")
        if self.rotating_counter > 360:
            self.rotating_counter = 0
            self.current_behavior = BEHAVIOR_STATE.SWITCHING_ROOMS
        else:
            self.eyes.scan_room()
            self.current_behavior = BEHAVIOR_STATE.SEARCHING

    def update_search(self):
        if self.current_behavior == BEHAVIOR_STATE.SEARCHING:
            self.search_for()
        elif self.current_behavior == BEHAVIOR_STATE.SWITCHING_ROOMS:
            self.go_to_room()

    def go_to_room(self):
        if self.path_course is None:
            self.path_course = self.pathfinder.find_path(self.location_coordinates[0])
            self.location_coordinates.pop(0)
        else:
            self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)
            self.move_to_next_node()


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
    TRAINING = 6
    SEARCHING = 7
    SWITCHING_ROOMS = 8
