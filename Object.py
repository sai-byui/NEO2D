import pygame

class Object(pygame.sprite.Sprite):

    """Objects are any items that are placed in NEO's environment which it can interact with

    name: the name of the object, string value
    color: string of color name
    size: an integer length
    weight: an integer value
    x: x coordinate int value
    y: y coordinate int value
    image: the string name of the image file
    """
    def __init__(self, name, color, weight, x, y, image):
        super(Object, self).__init__()

        self.name = name
        self.color = color
        self.weight = weight
        self.rect = pygame.Rect(x, y, 16, 16)
        self.x = x
        self.y = y
        obj_image = pygame.image.load(image)
        self.image = pygame.transform.scale(obj_image, (25, 25))
