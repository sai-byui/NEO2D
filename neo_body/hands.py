from agent import Agent


class Hands(Agent):
    """Holds objects and gathers info about weight, temp, etc."""

    def __init__(self):
        """default constructor"""
        super(Hands, self).__init__("hands")
        self.bot = self.share("neo", "bot")
        self.current_object_weight = None
        self.current_object_temperature = None

    def pick_up_object(self):
        """For now, only gets weight. Later, may determine softness, wetness, etc."""
        self.current_object_weight = self.ask("neo", "current_object").weight




