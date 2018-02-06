"""
The parent class of all environments. An environment serves as a interface where agents can share objects
with each other. All objects in an environment are accessible to any agent that knows about the environment
"""


class Environment:

    def __init__(self):
        self.objects = {}
        self.agents = {}

    def get_object(self, object_name):
        if object_name in self.objects:
            return self.objects[object_name]

    def add_object(self, object_name, item):
        self.objects[object_name] = item

    def update_object(self, object_name, item):
        self.objects[object_name] = item

    def remove_object(self, object_name):
        if object_name in self.objects:
            self.objects.pop(object_name)

    def add_agent(self, agent_name, agent):
        self.agents[agent_name] = agent
