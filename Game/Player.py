import numpy as np
import pygame as pg

from settings import RESOLUTION, MAX_SPEED, PLAYER_VISION_RANGE

vec = pg.math.Vector2


# Thruster motions courtesy of
# https://stackoverflow.com/questions/48856922/pygame-how-to-make-sprite-move-in-the-direction-its-facing-with-vectors
class Player(pg.sprite.Sprite):
    def __init__(self, x, y, img, brain):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.original_image = self.image
        self.position = vec(x, y)
        self.rect = self.image.get_rect(center=self.position)
        self.vel = vec(0, 0)
        self.acceleration = vec(0.1, 0.0)
        self.angle_speed = 0
        self.angle = 0
        self.score = 0.0
        self.radius = 5
        self.curr_img = 0
        self.dead = False
        self.brain = brain
        self.time_alive = 0
        self.moved = 0.0
        self.turned = 0.0
        self.closest_asteroid = None

    def update(self):
        # max speed
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.position += self.vel
        self.rect.center = self.position
        self.stabilize()  # Return to a resting position gradually

        self.time_alive += 1

    def propagate(self, inputs):
        self.brain.outputs = []
        inputs.append(self.angle)
        if np.linalg.norm(inputs) == 0:
            self.brain.calculate(inputs)
        else:
            self.brain.calculate(list(inputs / np.linalg.norm(inputs)))
        return self.brain.outputs.index(max(self.brain.outputs))

    def accelerate(self):
        self.vel += self.acceleration
        self.moved += 1

    def decelerate(self):
        self.vel -= self.acceleration
        self.moved += 0.5

    def rotate_counter_clockwise(self):
        self.angle_speed = -5
        self.rotate()
        self.turned += 1

    def rotate_clockwise(self):
        self.angle_speed = 5
        self.rotate()
        self.turned += 1

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
        self.vel[0] *= 0.985
        self.vel[1] *= 0.985

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

    def die(self):
        self.dead = True
