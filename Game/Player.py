import pygame as pg
from pygame.locals import *
from shapely.geometry import LineString

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
        self.acceleration = vec(0.2, 0.0)
        self.angle_speed = 0
        self.angle = 0
        self.score = 0.0
        self.radius = 5
        self.curr_img = 0
        self.vision = {}
        self.dead = False
        self.brain = brain
        self.time_alive = 0

    def update(self):
        # max speed
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.position += self.vel
        self.rect.center = self.position
        self.stabilize()  # Return to a resting position gradually

        self.update_vision()
        self.time_alive += 1

    def propagate(self, inputs):
        self.brain.outputs = []
        ins = list(inputs.values())
        ins.append(self.angle / 360.0)
        self.brain.calculate(ins)
        return self.brain.outputs.index(max(self.brain.outputs))

    def accelerate(self):
        self.vel += self.acceleration

    def decelerate(self):
        self.vel -= self.acceleration

    def rotate_counter_clockwise(self):
        self.angle_speed = -5
        self.rotate()

    def rotate_clockwise(self):
        self.angle_speed = 5
        self.rotate()

    def update_vision(self):
        center = self.rect.center
        x = center[0]
        y = center[1]

        self.vision["N"] = [center, (x, y - PLAYER_VISION_RANGE)]
        self.vision["E"] = [center, (x + PLAYER_VISION_RANGE, y)]
        self.vision["S"] = [center, (x, y + PLAYER_VISION_RANGE)]
        self.vision["W"] = [center, (x - PLAYER_VISION_RANGE, y)]

        self.vision["NE"] = [center, (x + PLAYER_VISION_RANGE, y - PLAYER_VISION_RANGE)]
        self.vision["SE"] = [center, (x + PLAYER_VISION_RANGE, y + PLAYER_VISION_RANGE)]
        self.vision["SW"] = [center, (x - PLAYER_VISION_RANGE, y + PLAYER_VISION_RANGE)]
        self.vision["NW"] = [center, (x - PLAYER_VISION_RANGE, y - PLAYER_VISION_RANGE)]

        # self.vision["N"] = LineString([center, (x, y - PLAYER_VISION_RANGE)])
        # self.vision["E"] = LineString([center, (x + PLAYER_VISION_RANGE, y)])
        # self.vision["S"] = LineString([center, (x, y + PLAYER_VISION_RANGE)])
        # self.vision["W"] = LineString([center, (x - PLAYER_VISION_RANGE, y)])
        #
        # self.vision["NE"] = LineString([center, (x + PLAYER_VISION_RANGE, y - PLAYER_VISION_RANGE)])
        # self.vision["SE"] = LineString([center, (x + PLAYER_VISION_RANGE, y + PLAYER_VISION_RANGE)])
        # self.vision["SW"] = LineString([center, (x - PLAYER_VISION_RANGE, y + PLAYER_VISION_RANGE)])
        # self.vision["NW"] = LineString([center, (x - PLAYER_VISION_RANGE, y - PLAYER_VISION_RANGE)])

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

    def die(self):
        self.dead = True
