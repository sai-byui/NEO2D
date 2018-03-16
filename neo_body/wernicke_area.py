from agent import Agent
import sqlite3



class Wernicke_Area(Agent):
    """This agent translates queries from natural language into SQL.
     Sentences are searched for key words such as adjectives and attributes(ex. "red": color)
     that neo recognizes in its database."""

    def __init__(self):
        """default constructor"""
        super(Wernicke_Area, self).__init__("wernicke_area")

        self.original_sentence = None
        self.query = None
        self.word_array = []
        self.qualifier_list = []
        self.location_list = []
        self.select_statement = None
        self.from_statement = None
        self.where_statement = None
        self.sql_statement = None
        self.correct_syntax = True
        self.answer_unknown = False
        self.location_coordinates = None
        self.cursor = None
        self.next_behavior = None
        # search variables
        self.search_all = False
        self.search_attribute_type = None
        self.search_adjective = None
        self.search_category = None

        #tracks behavior based on command passed
        self.next_behavior = None

    def analyze_query(self):
        self.reset_variables()
        self.original_sentence = self.ask("neo", "sentence")
        self.word_array = self.original_sentence.split()
        self.find_qualifiers()
        self.determine_inter()
        self.determine_table()
        self.create_where_statement()
        if self.correct_syntax:
            self.form_sql_statement()
        self.reset_qualifiers()

    def create_select_statement(self):
        self.select_statement = "SELECT object_name "

    def create_where_statement(self):
        """filters which objects are selected by using the set of qualifying attributes("red", "heavy", etc.) """
        self.where_statement = "WHERE "
        self.where_statement += "od.adjective_id IN ({0});".format(", ".join(repr(e) for e in self.qualifier_list))

    def determine_inter(self):
        """finds which question word is being used, more words will be added in future versions"""

        if self.word_array[0].lower() == "which":
            self.create_select_statement()
        else:
            self.correct_syntax = False

    def determine_table(self):
        self.from_statement = "FROM objects o INNER JOIN object_description od ON o.object_id = od.object_id "

    def find_qualifiers(self):
        """ searches each word in the sentence to determine if it is an adjective word"""

        conn = sqlite3.connect('neo_test.db')
        cursor = conn.cursor()
        for word in self.word_array:
            cursor.execute("SELECT adjective_id FROM ADJECTIVES WHERE adjective_name = ?", (word,))
            result = cursor.fetchone()
            if result:
                self.qualifier_list.append(result[0])
        # if we didn't find any adjectives that Neo recognizes, the answer is unknown
        if not self.qualifier_list:
                self.answer_unknown = True

        conn.close()

    def form_sql_statement(self):
        self.sql_statement = self.select_statement + self.from_statement + self.where_statement

    def reset_qualifiers(self):
        self.qualifier_list.clear()

    def reset_variables(self):
        self.query = None
        self.word_array = []
        self.qualifier_list = []
        self.select_statement = None
        self.from_statement = None
        self.where_statement = None
        self.sql_statement = None
        self.correct_syntax = True
        self.answer_unknown = False

    def parse_command(self, command):
        self.location_list.clear()
        conn = sqlite3.connect('neo_test.db')
        cursor = conn.cursor()
        word_array = command.split()
        for word in word_array:
            cursor.execute("SELECT FUNCTION_CALL FROM VERBS WHERE VERB_NAME LIKE ?", (word.lower() + '%',))
            result = cursor.fetchone()
            if result:
                method = getattr(Wernicke_Area, result[0])
                conn.close()
                method(self, command)
                break
            # if word == "search":
            #     self.search_for_objects()
            #     break
            # else:
            #     cursor.execute("SELECT location_id FROM LOCATIONS WHERE location_name LIKE ?", (word.lower() + '%',))
            #     result = cursor.fetchone()
            #     if result:
            #         self.location_list.append(result[0])
            #         print(self.location_list[0])
            #         self.determine_location(cursor)




    def go_to(self, command):
        conn = sqlite3.connect('neo_test.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT LOCATION_X, LOCATION_Y FROM LOCATIONS WHERE LOCATION_ID = ?""", (self.location_list[0],))
        result = cursor.fetchone()
        self.location_coordinates = result
        self.next_behavior = 8

        print(result)

    def search(self, command):
        conn = sqlite3.connect('neo_test.db')
        cursor = conn.cursor()
        self.search_all = False
        # this tells neo to start searching, see class BEHAVIOR_STATE in neo.py
        self.next_behavior = 7
        word_array = command.split()
        for word in word_array:
            cursor.execute("""SELECT ATTRIBUTE_NAME
                          FROM ATTRIBUTES a JOIN ADJECTIVE_TYPE at ON a.ATTRIBUTE_ID = at.ATTRIBUTE_ID
                          JOIN ADJECTIVES ad ON ad.ADJECTIVE_ID = at.ADJECTIVE_ID
                          WHERE ADJECTIVE_NAME = ?""", (word.lower(),))
            result = cursor.fetchone()
            if result:
                self.search_attribute_type = result[0]
                self.search_adjective = word

            if word.lower() == 'object' or word.lower() == 'objects':
                self.search_all = True
                break

            if self.search_all == False:
                cursor.execute("""SELECT OBJECT_NAME FROM OBJECTS WHERE OBJECT_NAME = ?""", (word.lower(),))
                object = cursor.fetchone()
                if object:
                    self.search_category = object[0]
        print("adjective: {} Attribute: {} category: {}".format(self.search_adjective, self.search_attribute_type, self.search_category))
        self.next_behavior = 7
        conn.close()

    # def null_function(self):
    #     print("successfully called function")
    #     self.location_coordinates = (500, 200)



