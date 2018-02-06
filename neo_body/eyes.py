from agent import Agent


class Eyes(Agent):
    """views objects and gathers visual information"""

    def __init__(self):
        """default constructor"""
        super(Eyes, self).__init__("eyes")
        self.bot = self.share("neo", "bot")
        self.current_object_color = None
        self.num_vis_obj = 0
        self.visible_object_list = []

    def look_at_object(self):
        """Gets color, later might get shape, visible textures, shininess, patterns, etc."""
        self.determine_color()

    def determine_color(self):
        """For now, simply returns the color string of an object."""
        self.current_object_color = self.ask("neo", "current_object").color

    def scan_room(self):
        """Checks if the 'bullets' are reloaded, then fires a raycast as a bullet"""
        if self.bot.reloaded():
            bullet_list = self.environment.get_object("bullet_list")
            bullet_list.add(self.bot.scan_ray_center())
