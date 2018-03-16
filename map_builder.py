import pygame

from agent import Agent
from Object import Object


class MapBuilder(Agent):
    """creates the wall sprites for the game and sets up the node graph used for path finding"""

    def __init__(self, environment=None):
        super(MapBuilder, self).__init__("map_builder", environment)
        self.wall_list = self.environment.get_object("wall_list")
        self.object_list = self.environment.get_object("object_list")
        self.map_with_nodes = []  # the map list that will have node positions inserted into it.
        self.node_list = []  # the list of each node found in our map
        self.node_step = 6  # determines how many spaces are between each node in the graph
        self.GRID_INCREMENT = 12  # determines how much space is between wall blocks and nodes
        self.screen_width = self.ask("game_manager", "screen_width")

    def convert_map_to_2d_array(self):
        """changes the map from list to 2d array in order to check for node connections"""

        multidimensional_map_array = []
        for y, line in enumerate(self.map_with_nodes):
            line_list = []
            for x, letter in enumerate(line):
                line_list.append(letter)
            # print(line_list)
            multidimensional_map_array.append(line_list)
        return multidimensional_map_array

    def create_node_graph(self):
        self.form_nodes()
        self.form_node_connections()

    def form_nodes(self):
        """creates the nodes of our path finding graph based on their x and y coordinates"""
        x = y = matrix_position_counter = 0
        # go through the map text and look for "N", create a node for each one found
        for row in self.map_with_nodes:
            for column in row:
                if column == "N":
                    node = Node(matrix_position_counter, x, y, None)
                    # add the new node to our list
                    self.node_list.append(node)
                x += 12
                matrix_position_counter += 1
            y += 12
            x = 0

    def form_node_connections(self):
        """goes through the 2d array to find any nodes that are not blocked by walls so connections can be formed.

        When each node of the map is created, it is given an id number that corresponds to its physical location
        on the map. For example the node in the top left corner would have an id number less than a node in the
        bottom right. These id numbers allow us to mathematically link nodes together. """

        multidimensional_array_map = self.convert_map_to_2d_array()
        # for each node we check 8 directions (Top, Top Right, Right, etc.) for neighboring nodes to connect to.
        # if the node exists in that position we create a connection to it
        for node in self.node_list:
            x = int(node.x / self.GRID_INCREMENT)
            y = int(node.y / self.GRID_INCREMENT)
            direction = 1
            while direction <= 8:
                counter = 1
                is_clear = True
                # Direction starts at top above the current node and moves in a clockwise direction
                if direction == 1:
                    dy = -1
                    dx = 0
                elif direction == 2:
                    dy = -1
                    dx = 1
                elif direction == 3:
                    dy = 0
                    dx = 1
                elif direction == 4:
                    dy = 1
                    dx = 1
                elif direction == 5:
                    dy = 1
                    dx = 0
                elif direction == 6:
                    dy = 1
                    dx = -1
                elif direction == 7:
                    dy = 0
                    dx = -1
                elif direction == 8:
                    dy = -1
                    dx = -1

                # these variables help us increment through the matrix
                inc_dy = dy
                inc_dx = dx
                # we check our matrix for any wall objects ('W') that exist between our node and the neighboring
                # node. If there are no walls in between, then the path is clear and we can add the node to our list of
                # connections.
                while counter <= self.node_step:
                    if multidimensional_array_map[y + dy][x + dx] != 'W':
                        if counter != self.node_step:
                            dy += inc_dy
                            dx += inc_dx
                        counter += 1
                    else:
                        is_clear = False
                        break
                if is_clear:
                    # using math, we determine that the id of the node that is connected to this node has
                    # the value of (current position + or - the direction we came from)
                    node_connection_number = (y + dy) * (self.screen_width / self.GRID_INCREMENT) + (x + dx)
                    # print(node_connection_number)
                    node.connections.append(node_connection_number)
                direction += 1

    def insert_nodes_into_map(self):
        """iterate through our starting map and look for spaces where we can insert nodes.

         Nodes are represented by the letter N and wall symbols are represented by W. We place a node every certain
         number of spaces, determined by the node step.
         """
        for y, line in enumerate(level_map):
            if y % self.node_step == 0:
                letter_list = []
                for x, letter in enumerate(line):

                    if x % self.node_step == 0 and letter != 'W':
                        letter = 'N'
                    letter_list.append(letter)
                node_line = ''.join(letter_list)
                self.map_with_nodes.append(node_line)
            else:
                self.map_with_nodes.append(line)

    def build_arena(self):
        self.construct_walls()
        self.insert_nodes_into_map()
        self.create_node_graph()

    def construct_walls(self):
        """converts the map string into actual wall objects for the game"""
        # Parse the level_map string. if a "W" is found create a Wall object
        x = y = 0
        for row in level_map:
            for col in row:
                if col == "W":
                    wall = Wall(x, y, 14, 14)
                    self.wall_list.add(wall)

                x += self.GRID_INCREMENT
            y += self.GRID_INCREMENT
            x = 0

    def insert_objects(self):
        test_object = Object('apple', 'green', 1, 450, 375, 'green_apple.jpg')
        self.object_list.add(test_object)  # insert test object into environment
        test_object2 = Object('apple', 'red', 1, 600, 375, 'apple.png')
        self.object_list.add(test_object2)  # insert test object into environment

        # There's a problem where NEO does not check behind objects - i.e., the 3 above


level_map = []
f = open('house1.txt', 'r')

for line in f:
    level_map.append(line.strip())


class Wall(pygame.sprite.Sprite):
    """the blocks that define the layout of the map"""
    def __init__(self, x, y, length, width):
        super(Wall, self).__init__()
        self.image = pygame.Surface([length, width])
        self.rect = pygame.Rect(x, y, length, width)
        self.image.fill((255, 255, 255))  # this makes the blocks white


class Node:
    """a data container that holds its x and y coordinates as well as a list of other nodes it is connected to"""

    def __init__(self, name, x, y, connections):

        self.name = name  # the id number of the node, used to identify each node when path finding
        self.x = x  # the node's x coordinate
        self.y = y  # the node's y coordinate
        self.connections = []  # an integer array holding all the id numbers of nodes it is connected to

        # this variable keeps track of which node preceded it in our path
        self.previous_node = None

        # value for A* algorithm
        self.f = 0
        self.g = 0

        if connections is None:
            return
        # if an array of connection numbers has been passed in, add them to our connection array
        for i in range(len(connections) - 1):
            self.connections += [connections[i]]
            print("connection: " + connections[i])
