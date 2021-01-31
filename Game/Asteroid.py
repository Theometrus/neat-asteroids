import random

import pygame as pg
from sympy import Circle, Point

from settings import RESOLUTION

vec = pg.math.Vector2


class Asteroid(pg.sprite.Sprite):
    def __init__(self, img):
        pg.sprite.Sprite.__init__(self)
        self.vel = vec(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
        self.image = img
        self.original_image = img
        self.position = self.spawn_out_of_screen()
        self.rect = self.image.get_rect(center=self.position)
        self.angle = 0
        self.angle_speed = random.uniform(-1.0, 1.0)
        self.circle = None
        self.radius = 30

    def spawn_out_of_screen(self):
        spawn_zones = [
            vec(random.uniform(0, RESOLUTION[0]), -30),
            vec(random.uniform(0, RESOLUTION[0]), RESOLUTION[1] + 30),
            vec(-30, random.uniform(0, RESOLUTION[1])),
            vec(RESOLUTION[0] + 30, random.uniform(0, RESOLUTION[1])),
        ]
        return random.choice(spawn_zones)

    def update(self):
        self.position += self.vel
        self.rect.center = self.position
        self.angle += self.angle_speed
        self.image = pg.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.update_vision_circle()

    def update_vision_circle(self):
        self.circle = Circle(Point(self.rect.x, self.rect.y), self.radius)

