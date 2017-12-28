from agent import Agent
import sqlite3


class Wernicke_Area(Agent):
    """This agent forms the query from natural language into SQL"""

    def __init__(self):
        """default constructor"""
        super(Wernicke_Area, self).__init__("wernicke_area")

        self.original_sentence = None
        self.query = None
        self.word_array = []
        self.qualifier_list = []
        self.select_statement = None
        self.from_statement = None
        self.where_statement = None
        self.sql_statement = None
        self.correct_syntax = True
        self.answer_unknown = False


    def analyze_query(self):
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
        self.where_statement = "WHERE "
        self.where_statement += "od.adjective_id IN ({0});".format(", ".join( repr(e) for e in self.qualifier_list))

    def determine_inter(self):
        if self.word_array[0].lower() == "which":
            self.create_select_statement()
        else:
            self.correct_syntax = False

    def determine_table(self):
        self.from_statement = "FROM objects o INNER JOIN object_description od ON o.object_id = od.object_id "

    def find_qualifiers(self):
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
        self.sql_statement = self.select_statement + self.from_statement +self.where_statement

    def reset_qualifiers(self):
        self.qualifier_list.clear()


