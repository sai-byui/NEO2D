from neo_body.agent import Agent
from neo_body.eyes import Eyes
from neo_body.hands import Hands
from neo_body.memory import Memory
from neo_body.mouth import Mouth
from neo_body.legs import Legs
from neo_body.wernicke_area import Wernicke_Area
from enum import Enum


class brain(Agent):
    """The driver Agent of the program, manages all other agents. The consciousness of NEO"""

    def __init__(self, environment):
        """default constructor"""
        super(brain, self).__init__("brain", environment)
        self.CURRENT_STATE = BEHAVIOR_STATE.SCANNING
        self.facing_direction = "RIGHT"
        self.finished = False
        self.position = 100
        self.sentence = None
        self.sql_statement = None
        self.list_of_objects = None
        self.current_object_name = None
        self.uninspected_objects = []
        self.eyes = Eyes()
        self.hands = Hands()
        self.legs = Legs()
        self.memory = Memory()
        self.mouth = Mouth()
        self.wernicke_area = Wernicke_Area()



    def determine_object_name(self):
        self.current_object_name = self.uninspected_objects[0].name
        self.uninspected_objects.pop(0)

    def find_objects(self, query):
        self.sql_statement = "SELECT OBJECT_NAME FROM OBJECTS WHERE OBJECT_COLOR = '" + query + "';"
        self.memory.recall_objects()
        self.list_of_objects = self.ask("memory", "short_term_memory")
        self.mouth.list_similar_objects()

    def scan_room(self):
        self.eyes.scan_area()
        self.mouth.report_visible_objects()

    def run_learning_program(self):
        if self.CURRENT_STATE == BEHAVIOR_STATE.SCANNING:
            self.scan_room()
            self.uninspected_objects = self.ask("eyes", "visible_object_list")
            self.CURRENT_STATE = BEHAVIOR_STATE.APPROACHING
        elif self.CURRENT_STATE == BEHAVIOR_STATE.APPROACHING:
            while self.position != self.uninspected_objects[0].position:
                self.legs.walk()
                self.position = self.ask("legs", "position")
                self.mouth.state_current_position()
            self.CURRENT_STATE = BEHAVIOR_STATE.INSPECTING
        elif self.CURRENT_STATE == BEHAVIOR_STATE.INSPECTING:
            self.hands.pick_up_object()
            self.eyes.look_at_object()
            self.determine_object_name()
            self.memory.memorize()

            if self.uninspected_objects:
                self.CURRENT_STATE = BEHAVIOR_STATE.APPROACHING
            else:
                self.finished = True
        else:
            self.CURRENT_STATE = BEHAVIOR_STATE.FINISHED
            self.finished = True

    def sentence_test(self, sentence):
        self.sentence = sentence
        self.wernicke_area.analyze_query()
        if self.ask("wernicke_area", "correct_syntax"):
            self.sql_statement = self.ask("wernicke_area", "sql_statement")
            self.memory.recall_objects()
            self.list_of_objects = self.ask("memory", "short_term_memory")
        self.mouth.list_similar_objects()




class BEHAVIOR_STATE(Enum):
    SCANNING = 1
    APPROACHING = 2
    INSPECTING = 3
    FINISHED = 4
    PATH_FINDING = 5