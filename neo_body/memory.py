from enum import Enum
import sqlite3
import os

from agent import Agent


class Memory(Agent):
    """Keeps track of objects NEO has interacted with and their associations based on attributes using a SQLITE DB.

    NEO has three main tables: objects, adjectives, and a linking table between them. objects hold names of the objects
    that NEO interacts with. Adjectives hold descriptive words and what category that adjective belongs to (ex. 'red' is
    a category of color). The linking table allows NEO to associate objects with their attributes."""

    def __init__(self):
        """default constructor"""
        super(Memory, self).__init__("memory")
        self.current_object_color = None
        self.current_object_name = None
        self.short_term_memory = None
        self.current_object_weight = None
        self.current_object_x_pos = None
        self.current_object_y_pos = None
        self.current_x_pos = None
        self.current_y_pos = None
        self.current_row_index = 1
        self.colors = {}
        self.weights = {}
        self.create_object_memory()

    def memorize(self):
        """Writes the attributes of the current object to the database"""
        self.current_object_color = self.ask("eyes", "current_object_color")
        self.current_object_name = self.ask("neo", "current_object").name
        self.current_object_x_pos = self.ask("neo", "current_object").x
        self.current_object_y_pos = self.ask("neo", "current_object").y
        self.current_object_weight = self.ask("hands", "current_object_weight")
        self.store_object_info()

    def store_object_info(self):
        """stores the object into memory and links the object to any attributes that the object has"""
        conn = sqlite3.connect('neo_test.db')

        cursor = conn.cursor()

        # insert the object into the objects table along with its attributes
        cursor.execute("INSERT INTO OBJECTS (object_name) "
                       "VALUES (:name)",
                       {'name': self.current_object_name})

        # insert the color into the adjective table
        cursor.execute("INSERT OR IGNORE INTO ADJECTIVES (adjective_name) VALUES (:name)",
                       {'name': self.current_object_color})

        # get the id of the adjective so we can link it to the object in the linking table
        cursor.execute("SELECT adjective_id FROM ADJECTIVES WHERE adjective_name = ?", (self.current_object_color,))
        adjective_id = cursor.fetchone()[0]

        # get the id of the object so we can link it to the object in the linking table
        cursor.execute("SELECT object_id FROM OBJECTS WHERE object_name = ?", (self.current_object_name,))
        object_id = cursor.fetchone()[0]

        # make the connection between the adjective and its relation to the object
        cursor.execute("""INSERT INTO OBJECT_DESCRIPTION (object_id, adjective_id)
                          VALUES (
                          ?,
                          ?)""", (object_id, adjective_id,))
        # cursor.execute("SELECT * FROM OBJECT_DESCRIPTION")
        # print(cursor.fetchall())

        cursor.execute("""SELECT * FROM OBJECTS WHERE OBJECT_NAME = :name""", {'name': self.current_object_name})
        print(cursor.fetchone())

        conn.commit()
        conn.close()

    def create_object_memory(self):
        """creates neo's DB tables the first time neo is initialized or in the event that the DB file is not found"""

        if not os.path.isfile('./neo_test.db'):
            conn = sqlite3.connect('neo_test.db')

            cursor = conn.cursor()

            # cursor.execute("""DROP TABLE IF EXISTS OBJECTS""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS OBJECTS
                              (
                               object_id INTEGER PRIMARY KEY,
                               OBJECT_NAME TEXT
                               )""")

            # this table hold all the commands that neo is familiar with
            cursor.execute("""CREATE TABLE IF NOT EXISTS VERBS
              (
               VERB_ID INTEGER PRIMARY KEY,
               VERB_NAME TEXT
               )""")

            # This table holds quantifier info (some, all, both, etc.)
            cursor.execute("""CREATE TABLE IF NOT EXISTS QUANTIFIERS
              (
               q_id INTEGER REFERENCES OBJECTS (object_id),
               q_name TEXT
               )
              """)

            # table for holding adjective keywords(red, heavy, soft etc.)
            # cursor.execute("""DROP TABLE IF EXISTS ADJECTIVES""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS ADJECTIVES
                                  (
                                   adjective_id INTEGER PRIMARY KEY ,
                                   adjective_name UNIQUE
                                  )""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS ATTRIBUTES
                (
                 ATTRIBUTE_ID INTEGER PRIMARY KEY ,
                 ATTRIBUTE_NAME TEXT UNIQUE NOT NULL
                 )""")

            # comparators are used for neo to compare similar attributes
            # of different objects
            cursor.execute("""CREATE TABLE IF NOT EXISTS COMPARATORS
              (
               COMPARATOR_ID INTEGER PRIMARY KEY,
               LESS_THAN TEXT,
               GREATER_THAN TEXT,
               EQUAL TEXT
               )""")

            # this table links which attributes are connected to certain comparative words
            # ex.('heavier' is related to the attribute 'weight')
            cursor.execute("""CREATE TABLE IF NOT EXISTS ATTRIBUTE_COMPARATORS
              (
               ATTRIBUTE_ID INTEGER REFERENCES ATTRIBUTES (ATTRIBUTE_ID),
               COMPARATOR_ID INTEGER REFERENCES COMPARATORS (COMPARATOR_ID)
               )""")

            # this table holds category keywords (food, liquid, weapon, etc.)
            cursor.execute("""CREATE TABLE IF NOT EXISTS CATEGORIES
                (
                 CATEGORY_ID INTEGER PRIMARY KEY ,
                 CATEGORY_NAME TEXT UNIQUE NOT NULL
                 )""")

            # links categories to objects (an apple is a fruit, food, plant, etc.)
            cursor.execute("""CREATE TABLE IF NOT EXISTS OBJECT_CATEGORIES
              (
               OBJECT_ID INTEGER REFERENCES OBJECTS (OBJECT_ID),
               CATEGORY_ID INTEGER REFERENCES CATEGORIES (CATEGORY_ID)
               )""")

            # create linking table between objects and adjectives
            # the attribute value holds the value for the particular attribute of each object
            # ex. apple, color, 'red'
            # cursor.execute("""DROP TABLE IF EXISTS OBJECT_DESCRIPTION""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS OBJECT_DESCRIPTION
                              (
                               object_id INTEGER REFERENCES OBJECTS (object_id) ON DELETE CASCADE ,
                               attribute_id INTEGER REFERENCES ADJECTIVES (adjective_id) ON DELETE CASCADE,
                               attribute_value
                              )""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS LOCATIONS
                                (
                                LOCATION_ID INTEGER PRIMARY KEY,
                                LOCATION_NAME TEXT NOT NULL,
                                LOCATION_X INTEGER NOT NULL,
                                LOCATION_Y INTEGER NOT NULL
                                )""")

        # this table links the adjective key words with the attribute key words
        # (ex. the adjective 'red' is a type of the attribute 'color'
            # cursor.execute("""DROP TABLE IF EXISTS ADJECTIVE_TYPE""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS ADJECTIVE_TYPE
                                  (
                                   attribute_id INTEGER REFERENCES ATTRIBUTES (attribute_id),
                                   adjective_id INTEGER REFERENCES ADJECTIVES (adjective_id)
                                  )""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS VERB_CATEGORIES
              (
               VERB_ID INTEGER REFERENCES VERBS (VERB_ID),
               CATEGORY_ID INTEGER REFERENCES CATEGORIES (CATEGORY_ID)
               )""")

            conn.commit()
            conn.close()

    def recall_objects(self):
        """uses the sql statement created by the Wernicke Area class to recall object of a certain attribute"""
        statement = self.ask("neo", "sql_statement")
        conn = sqlite3.connect('neo_test.db')

        cursor = conn.cursor()

        cursor.execute(statement)

        self.short_term_memory = cursor.fetchall()
        conn.close()

    def save_location(self, location_name):
        # get the x and y coordinates from the legs class
        self.current_x_pos = self.ask("legs", 'x_pos')
        self.current_y_pos = self.ask("legs", 'y_pos')
        print("x_pos {} y_pos {}".format(self.current_x_pos, self.current_y_pos))

        conn = sqlite3.connect('neo_test.db')

        cursor = conn.cursor()

        cursor.execute("INSERT INTO LOCATIONS (LOCATION_NAME, LOCATION_X, LOCATION_Y) "
         "VALUES (:name, :x, :y)", {'name': location_name, 'x': self.current_x_pos, 'y': self.current_y_pos})

        cursor.execute("SELECT * FROM LOCATIONS")
        print(cursor.fetchall())

        conn.commit()
        conn.close()






