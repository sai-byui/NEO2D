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
from neo_body.searcher import Searcher

from bot import Bot
from raycast import RayCaster
from pathfinder import Pathfinder

from agent import Agent

from copy import deepcopy


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
        self.searcher = Searcher()

        self.current_object = None

        # these coordinates tell the agent how far away the object is
        self.object_coordinates = None
        self.distance_from_object = 0
        self.current_position = 0

        self.path_course = []
        self.path_found = False
        self.next_node_coordinates = None

        # variables for A.I. object inspecting behavior
        self.inspecting = False
        self.detected_objects = []
        self.uninspected_objects = []
        self.object_under_inspection = None

        self.previous_behavior = BEHAVIOR_STATE.TRAINING
        self.current_behavior = BEHAVIOR_STATE.TRAINING
        self.pathfinder = Pathfinder()

        #search variables
        self.rotating_counter = 0
        self.location_coordinates = self.ask("memory", "location_coordinates")
        self.unsearched_rooms = self.location_coordinates

        self.sql_statement = None


    def determine_object_match(self):
        adjective = self.searcher.search_adjective
        attribute = self.searcher.search_attribute_type
        object_type = self.searcher.search_object_category
        object_attribute = getattr(self.detected_objects[0], attribute)

        if object_attribute == adjective and self.detected_objects[0].name == object_type:
            print("Found " + adjective + " " + object_type)
            # reset our rotating counter for the next time we scan the room
            self.rotating_counter = 0
            self.current_behavior = BEHAVIOR_STATE.APPROACHING
        else:
            print("This object is not what I'm looking for")
            self.detected_objects.pop(0)




    def filter_detected_objects(self):
        """Decides whether detected objects(currently just 1 at a time) have been inspected before"""
        for obj in self.detected_objects:
            self.sql_statement = "SELECT * FROM objects"
            self.memory.recall_objects()
            if self.ask("memory", "short_term_memory"):
                self.detected_objects.remove(obj)
            else:
                self.uninspected_objects += [obj]
                self.detected_objects.remove(obj)

    def find_next_node(self):
        """finds the closest node in our path and removes nodes once they are reached"""
        if not (1 <= abs(self.rect.centerx - self.next_node_coordinates[0]) or 1 <= abs(
                    self.rect.centery - self.next_node_coordinates[1])) and self.path_course:
            self.path_course.pop(0)
            if self.path_course:
                self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)


    def make_decision(self):
        """Acts out decisions based on the current behavior state"""
        if self.current_behavior == BEHAVIOR_STATE.TRAINING:
            self.run_training()
        elif self.current_behavior == BEHAVIOR_STATE.SEARCHING:
            self.search_for()
        elif self.current_behavior == BEHAVIOR_STATE.SWITCHING_ROOMS:
            self.go_to_room()
        elif self.current_behavior == BEHAVIOR_STATE.SCANNING:
            self.scan_room()
        elif self.current_behavior == BEHAVIOR_STATE.PATH_FINDING:
            pass
        elif self.current_behavior == BEHAVIOR_STATE.APPROACHING:
            self.move_to_object()

        #always update our coordinates
        self.update_coordinates()
        # if not self.running_training:
        #     self.filter_detected_objects()
        #     self.determine_behavior()
        #     if self.current_behavior == BEHAVIOR_STATE.SCANNING:
        #         self.legs.rotate()
        #         self.angle = self.ask("legs", "angle")
        #         self.eyes.scan_room()
        #         # _thread.start_new_thread(self.mouth.speak, ("Scanning Room",))
        #     elif self.current_behavior == BEHAVIOR_STATE.PATH_FINDING:
        #         self.path_course = self.pathfinder.find_path(self.object_coordinates)
        #         self.path_found = True
        #         self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)
        #     elif self.current_behavior == BEHAVIOR_STATE.APPROACHING:
        #         if not self.path_course:
        #             self.path_found = False
        #             self.inspecting = True
        #             return
        #         self.find_next_node()
        #         self.move_to_next_node()
        #     elif self.current_behavior == BEHAVIOR_STATE.INSPECTING:
        #         # if not self.mouth.inspection_message_spoken:
        #         #     self.mouth.stopSentence()
        #         #     _thread.start_new_thread(self.mouth.speak, ("Inspecting Object",))
        #         #     self.mouth.inspection_message_spoken = True
        #         self.eyes.look_at_object()
        #         self.hands.pick_up_object()
        #         self.memory.memorize()
        #         self.inspecting = False
        #         self.uninspected_objects.remove(self.current_object)
        #         self.current_object = None
        # else:
        #     self.run_training()

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

    def move_to_object(self):
        if self.previous_behavior == BEHAVIOR_STATE.SEARCHING:
            if not self.path_found:
                object_coordinates = (self.detected_objects[0].x, self.detected_objects[0].y)
                self.update_coordinates()
                self.path_course = self.pathfinder.find_path(object_coordinates)
                # remove the room we are moving towards from the list of rooms we have visited
                self.path_found = True
                self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)
            else:
                if self.path_course:
                    self.find_next_node()
                    self.move_to_next_node()
                else:
                    print("reached object!")
                    if self.previous_behavior == BEHAVIOR_STATE.SEARCHING:
                        self.path_found = False
                        self.detected_objects.pop(0)
                        self.current_behavior = BEHAVIOR_STATE.TRAINING
                    else:
                        # inspect the object and save its attributes in memory
                        self.current_behavior = BEHAVIOR_STATE.INSPECTING

    def run_training(self):
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
                self.current_behavior = BEHAVIOR_STATE(self.current_behavior)
                # determine what our next behavior is and pass around needed variables
                if self.current_behavior == BEHAVIOR_STATE.SEARCHING:
                    self.previous_behavior = BEHAVIOR_STATE.SEARCHING
                    self.searcher.get_search_variables()

    def search_for(self):
        self.legs.rotate()
        self.rotating_counter += 1
        self.angle = self.ask("legs", "angle")
        if self.rotating_counter > 360:
            self.rotating_counter = 0
            self.previous_behavior = BEHAVIOR_STATE.SEARCHING
            self.current_behavior = BEHAVIOR_STATE.SWITCHING_ROOMS
        else:
            self.eyes.scan_room()
            self.current_behavior = BEHAVIOR_STATE.SEARCHING

    def go_to_room(self):
        # if NEO is searching for an object, go to the next room in the house that we haven't searched yet
        if self.previous_behavior == BEHAVIOR_STATE.SEARCHING:
            if not self.path_found:
                self.update_coordinates()
                # if we have already searched all the rooms of the house, end the search and notify
                # the user that the object was not found.
                if not self.unsearched_rooms:
                    print("House searched, could not find object")
                    # reset the list for the next time we search
                    self.unsearched_rooms = self.ask("memory", "location_coordinates")
                    self.current_behavior = BEHAVIOR_STATE.TRAINING
                else:
                    self.path_course = self.pathfinder.find_path(self.unsearched_rooms[0])
                    # remove the room we are moving towards from the list of rooms we have visited
                    self.unsearched_rooms.pop(0)
                    self.path_found = True
                    self.next_node_coordinates = (self.path_course[0].x, self.path_course[0].y)
            else:
                if self.path_course:
                    self.find_next_node()
                    self.move_to_next_node()
                else:
                    print("switched rooms!")
                    if self.previous_behavior == BEHAVIOR_STATE.SEARCHING:
                        self.current_behavior = BEHAVIOR_STATE.SEARCHING
                        self.path_found = False
                    else:
                       self.current_behavior = BEHAVIOR_STATE.TRAINING
        # Else NEO is not searching, just move to the room that the user has specified
        elif self.previous_behavior == BEHAVIOR_STATE.TRAINING:
            pass


    def scan_room(self):
        self.legs.rotate()
        self.angle = self.ask("legs", "angle")
        self.eyes.scan_room()

    def setup_bot_map(self):
        self.bot.wall_list = self.environment.get_object("wall_list")

    def update_coordinates(self):
        self.red_coordinate = (self.rect.x, self.rect.y)


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

# CODE FROM BOT_ARENA_3

# def shoot(self):
    #     if self.bot.reloaded():
    #         bullet_list = self.environment.get_object("bullet_list")
    #         if self.current_position == PilotCurrentPosition.LEFT:
    #             bullet_list.add(self.bot.shoot_right())
    #         elif self.current_position == PilotCurrentPosition.RIGHT:
    #             bullet_list.add(self.bot.shoot_left())
    #         elif self.current_position == PilotCurrentPosition.ABOVE:
    #             bullet_list.add(self.bot.shoot_down())
    #         elif self.current_position == PilotCurrentPosition.BELOW:
    #             bullet_list.add(self.bot.shoot_up())

# def determine_object_position(self):
    #     """"used to determine which direction the red player should turn to face object"""
    #     if self.red_coordinate[0] + MARGIN >= self.object_coordinates[0] >= MARGIN - self.red_coordinate[0]:
    #         # red player is above blue player
    #         if self.red_coordinate[1] < self.object_coordinates[1] - MARGIN:
    #             self.current_position = PilotCurrentPosition.ABOVE
    #
    #         # red player is below blue player
    #         elif self.red_coordinate[1] > self.object_coordinates[1] + MARGIN:
    #             self.current_position = PilotCurrentPosition.BELOW
    #         # red player is right of blue
    #         elif self.red_coordinate[0] > self.object_coordinates[0]:
    #             self.current_position = PilotCurrentPosition.RIGHT
    #         # red player is left of blue
    #         elif self.red_coordinate[0] < self.object_coordinates[0]:
    #             self.current_position = PilotCurrentPosition.LEFT

    # def is_healthy(self):
    #     return self.hit_points > 50

# def check_distance_from_object(self):
    #     self.update_coordinates()
    #     self.distance_from_object = \
    #         abs(self.object_coordinates[0] - self.red_coordinate[0]) + \
    #         abs(self.object_coordinates[1] - self.red_coordinate[1])
