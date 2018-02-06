from agent import Agent


class Pathfinder(Agent):
    """uses the A* path finding algorithm to determine the red_ai_pilot's movement"""

    def __init__(self):
        """sets up path finding variables for use in the A* algorithm"""
        super(Pathfinder, self).__init__("pathfinder")
        # nodes which we know the f cost for but have not yet searched
        self.open_list = []
        # nodes whose connections we have searched
        self.closed_list = []
        # we will stick our chain of nodes that form our final path in here
        self.final_path_list = []

        # the list of all the nodes we start with in our graph
        self.unvisited = []

        self.end_node = None
        self.current_node = None
        self.target = None
        self.red_coordinate = self.ask("neo", "red_coordinate")
        self.GRID_INCREMENT = self.ask("map_builder", "GRID_INCREMENT")
        self.NODE_STEP = self.ask("map_builder", "node_step")

        self.start_node = None
        self.start_node_index = None

    def determine_starting_point(self):
        """finds the node closest to NEO's position and sets it as the start node"""
        self.target = self.ask("neo", "red_coordinate")
        self.determine_goal()
        return self.end_node

    def determine_goal(self):
        """finds the closest node to the given target coordinates"""
        # for each node in our graph, we check the coordinates to see if it's "close enough" to our goal coordinates
        for node in self.unvisited:
            if self.GRID_INCREMENT * self.NODE_STEP >= abs(node.x - self.target[0]) and \
                                    self.GRID_INCREMENT * self.NODE_STEP >= abs(node.y - self.target[1]):
                print("matched coordinates with node# " + str(node.name))
                # use the matched node as the end node which we find the path to
                self.end_node = node
                # our next start node will be our current end_node for the next time we find a path
                self.start_node_index = self.unvisited.index(node)
                break

    def find_path(self, target_coordinates):
        """uses the A* algorithm to find the best path from starting point to the end position

        key variables:
        unvisited: the list of all the nodes we start with in our graph
        closed_list: nodes whose connections we have searched
        open_list: nodes which we know the f cost for but have not yet searched

        The find_path method works in the following steps:
            1. the first node in your open_list becomes your current node whose connections you are searching
            2. remove the current node from the open_list and place it into the closed_list
            3. for each connection to the current node, find the connected node in our unvisited list and determine its F cost
            4. once a node's F cost is determined, sort it into the open_list from lowest F cost to Highest
            5. when all the current node's connections have been checked, repeat steps 1 - 4 until your end goal is reached
            """
        # ask the map_builder for the entire graph of nodes which we will search through
        self.unvisited = self.ask("map_builder", "node_list")
        if self.start_node_index is None:
            self.start_node = self.determine_starting_point()
        else:
            self.start_node = self.unvisited[self.start_node_index]

        # find our end node based on the passed coordinates
        self.target = target_coordinates
        self.determine_goal()

        # reset our lists as empty
        self.open_list = []
        self.closed_list = []
        self.final_path_list = []

        # we set our start node as the current node and search it's connections
        self.closed_list.append(self.start_node)
        self.current_node = self.start_node

        # if we happen to already be at our end node, put our start node as the only one in the list and return
        if self.start_node.name == self.end_node.name:
            self.final_path_list.append(self.start_node)
            return

        # remove the starting node from our list
        self.unvisited.remove(self.start_node)

        # this will be false until we reach our goal
        path_found = False
        while not path_found:
            # loop through all of connections in our node object (ex. "190", "194", "198")
            for connection in self.current_node.connections:
                if path_found:
                    break
                    # find that corresponding node in the list of our unvisited nodes
                for unvisited_node in self.unvisited:
                    if unvisited_node.name == connection:
                        # once we find a match, we pass it in to our determine_cost method to find its f cost
                        determine_cost(self.current_node, unvisited_node, self.end_node)
                        # print("unvisited Node " + str(unvisited_node.name) + " f cost: " + str(unvisited_node.f))
                        # check to see if we have reached our goal node
                        if self.end_node.name == unvisited_node.name:
                            self.end_node = unvisited_node
                            self.end_node.previous_node = self.current_node
                            path_found = True
                            break
                            # now move the node from our unvisited list to our open list since we know its f cost
                        self.transfer_open_node(unvisited_node)

            if not path_found:
                # now we move on the the first node found in our open list, this is the most likely candidate
                # based on it's f cost.
                self.current_node = self.open_list.pop(0)
                self.closed_list.append(self.current_node)

        # Once we have found the path to the end node, will will place the linked nodes into a list to make it easier
        # to read our path. this setup is not necessary as we could just access the "previous_node" field directly, but
        # for this example we will organize it into a list
        while self.end_node.name != self.start_node.name:

            # insert the current node of our chain into the front of the list
            self.final_path_list.insert(0, self.end_node)

            # if our current node does not have a previous node to point to, exit the loop
            if not self.end_node.previous_node:
                break

            # move to the previous connected node
            self.end_node = self.end_node.previous_node

        # finally insert our start_node
        self.final_path_list.insert(0, self.start_node)

        return self.final_path_list

    def find_node_index(self, node):
        """searches our list of nodes and returns the index of the passed no"""
        node_name = node.name
        node_graph = self.unvisited
        for node in node_graph:
            if node.name == node_name:
                return self.node_graph.index(node)

    def transfer_open_node(self, unvisited_node):
        """removes a node from the unvisited list and adds it to the open list"""

        # first remove the node from the unvisited list
        self.unvisited.remove(unvisited_node)

        # link our node to the previous node we are coming from so we can keep track of our path
        unvisited_node.previous_node = self.current_node

        # now check if our open_list is empty, in which case we place it in the front
        if not self.open_list:
            self.open_list.append(unvisited_node)
            return

        # else we iterate through our list and place our unvisited node into the open_list based on it's f cost
        i = 0
        inserted = False
        for current_node in self.open_list:
            if unvisited_node.f < current_node.f:
                self.open_list.insert(i, unvisited_node)
                inserted = True
                break
            else:
                i += 1

        # if our node's f cost is the largest, insert it at the back
        if not inserted:
            self.open_list.append(unvisited_node)


def determine_cost(current_node, unvisited_node, end_node):
    """ uses the pythagorean theorem to determine the g and h cost of an unvisited node

        we determine the distance by measuring a straight line from our current node to our starting and ending node
        g = distance from the start node
        h = guess of how far we are from the end node
        f = total estimated cost
        """
    # determine the distance based on the difference in our x and y coordinates,
    # then add on the distance we already are from the start node
    unvisited_node.g = (((current_node.x - unvisited_node.x) ** 2 +
                         (current_node.y - unvisited_node.y) ** 2) ** .5) + current_node.g

    h = ((end_node.x - unvisited_node.x) ** 2 + (end_node.y - unvisited_node.y) ** 2) ** .5

    unvisited_node.f = unvisited_node.g + h
