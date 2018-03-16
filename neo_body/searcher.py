from agent import Agent


class Searcher(Agent):

    def __init__(self):
        # search variables
        self.search_adjective = None  # holds the adjective word we need to match in our search (red, heavy, etc.)
        self.search_attribute_type = None  # holds the attribute we need to search in order to find our adj match(color, etc.)
        self.search_object_category = None  # holds what type of object we are searching for (apple, fruit, etc.)
        self.unsearched_rooms = self.ask("memory", "location_coordinates")

    def get_search_variables(self):
        self.search_adjective = self.ask("wernicke_area", "search_adjective")
        self.search_attribute_type = self.ask("wernicke_area", "search_attribute_type")
        self.search_object_category = self.ask("wernicke_area", "search_category")

