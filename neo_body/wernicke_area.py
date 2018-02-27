from agent import Agent
import sqlite3


class Wernicke_Area(Agent):
    """This agent forms the query from natural language into SQL.
     Sentences are searched for key words such as attributes(ex. "red")
     that neo recognizes in its database. It then finds each object that contains that attribute."""

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
            if word == "search":
                self.search_for_objects()
                break
            else:
                cursor.execute("SELECT location_id FROM LOCATIONS WHERE location_name LIKE ?", (word.lower() + '%',))
                result = cursor.fetchone()
                if result:
                    self.location_list.append(result[0])
                    print(self.location_list[0])
                    self.determine_location(cursor)


        conn.close()

    def determine_location(self, cursor):
        cursor.execute("""SELECT LOCATION_X, LOCATION_Y FROM LOCATIONS WHERE LOCATION_ID = ?""", (self.location_list[0],))
        result = cursor.fetchone()
        self.location_coordinates = result
        print(result)

    def search_for_objects(self):
        pass



