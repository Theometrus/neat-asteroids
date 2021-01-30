import pygame as pg
from pygame.locals import *

from settings import RESOLUTION, MAX_SPEED

vec = pg.math.Vector2


# Thruster motions courtesy of
# https://stackoverflow.com/questions/48856922/pygame-how-to-make-sprite-move-in-the-direction-its-facing-with-vectors
class Player(pg.sprite.Sprite):
    def __init__(self, x, y, img):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.original_image = self.image
        self.position = vec(x, y)
        self.rect = self.image.get_rect(center=self.position)
        self.vel = vec(0, 0)
        self.acceleration = vec(0.2, 0.0)  # The acceleration vec points upwards.
        self.angle_speed = 0
        self.angle = 0

    def update(self):
        keys = pg.key.get_pressed()
        if keys[K_LEFT]:
            self.angle_speed = -5
            self.rotate()
        if keys[K_RIGHT]:
            self.angle_speed = 5
            self.rotate()

        # If up or down is pressed, accelerate the ship by
        # adding the acceleration to the velocity vector.
        if keys[K_UP]:
            self.vel += self.acceleration
        if keys[K_DOWN]:
            self.vel -= self.acceleration

        # max speed
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.position += self.vel
        self.rect.center = self.position
        self.stabilize()  # Return to a resting position gradually

    def rotate(self):
        # Rotate the acceleration vector.
        self.acceleration.rotate_ip(self.angle_speed)
        self.angle += self.angle_speed
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
        self.image = pg.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def stabilize(self):
        self.vel[0] *= 0.991
        self.vel[1] *= 0.991

    def wrap_around_screen(self):
        """Wrap around screen."""
        if self.position.x > RESOLUTION[0]:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = RESOLUTION[0]
        if self.position.y <= 0:
            self.position.y = RESOLUTION[1]
        if self.position.y > RESOLUTION[1]:
            self.position.y = 0
