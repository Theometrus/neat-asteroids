import itertools
import math
import os
import random

import pygame as pg
from shapely.geometry import LineString, Point

from Game.Asteroid import Asteroid
from Game.Bullet import Bullet
from Game.Player import Player
from settings import RESOLUTION, ASTEROID_COUNT


class Sandbox:
    def __init__(self, screen, brain):
        game_folder = os.path.dirname(__file__)
        img_folder = os.path.join(game_folder, 'sprites')

        self.bg = pg.image.load(os.path.join(img_folder, 'Space_Stars4.png'))
        self.bullet_img = pg.image.load(os.path.join(img_folder, 'bullet.png'))
        self.ast_imgs = [pg.image.load(os.path.join(img_folder, 'ast1.png'))]
        self.player_img = pg.image.load(os.path.join(img_folder, 'tile010.png'))

        self.player = Player(300, 200, self.player_img, brain)
        self.screen = screen
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.player_group.add(self.player)
        self.cooldown = 0

    def display(self):
        self.setup_background()

        self.bullets.draw(self.screen)
        self.asteroids.draw(self.screen)
        self.player_group.draw(self.screen)

    def tick(self):
        self.player.wrap_around_screen()

        self.remove_out_of_screen(self.bullets)
        self.remove_out_of_screen(self.asteroids)

        self.bullets.update()
        self.replenish_asteroids()
        self.asteroids.update()
        self.player.update()
        self.check_collisions()
        self.propagate_player()
        self.cooldown += 1

    def propagate_player(self):
        vision_inputs = {}

        for key, val in self.player.vision.items():
            vision_inputs[key] = 0.0

        for a in self.asteroids:
            for key, val in self.player.vision.items():
                i = a.circle.intersection(val)
                point = None

                # Shapely returns different types depending on the result, hence need these tests
                if type(i) is not LineString:
                    # One point of intersection
                    if type(i) is Point:
                        point = i.coords[0]

                    # Two points of intersection
                    else:
                        player_coords = self.player.rect.center
                        d1 = self.distance(i.geoms[0].coords[0], player_coords)
                        d2 = self.distance(i.geoms[1].coords[0], player_coords)
                        point = i.geoms[0].coords[0] if d1 < d2 else i.geoms[1].coords[0]

                if point is not None:
                    dist = self.distance(self.player.rect.center, point)
                    scaled_dist = 1 - (dist / val.length)  # Want the input to get stronger the closer the enemy is

                    if vision_inputs[key] < scaled_dist:
                        vision_inputs[key] = scaled_dist

        choice = self.player.propagate(vision_inputs)

        if choice == 0:
            self.player.accelerate()
        elif choice == 1:
            self.player.decelerate()
        elif choice == 2:
            self.player.rotate_clockwise()
        elif choice == 3:
            self.player.rotate_counter_clockwise()
        elif choice == 4:
            if self.cooldown % 30 == 0:  # Don't allow player to make bullet laser beams
                self.bullets.add(Bullet(self.player, self.bullet_img))

    def setup_background(self):
        brick_width, brick_height = self.bg.get_width(), self.bg.get_height()
        for x, y in itertools.product(range(0, 720, brick_width),
                                      range(0, 480, brick_height)):
            self.screen.blit(self.bg, (x, y))

    def remove_out_of_screen(self, sprites):
        count = 0

        for s in sprites:
            if s.position.x > RESOLUTION[0] + 50 or s.position.x < -50 or s.position.y <= -50 or s.position.y > \
                    RESOLUTION[1] + 50:
                sprites.remove(s)
                count += 1

        return count

    def replenish_asteroids(self):
        while len(self.asteroids) < ASTEROID_COUNT:
            self.asteroids.add(Asteroid(random.choice(self.ast_imgs)))

    def check_collisions(self):
        for a in self.asteroids:
            if pg.sprite.collide_circle(self.player, a):
                self.player.die()

            for b in self.bullets:
                if pg.sprite.collide_circle(a, b):
                    self.player.score += 1
                    self.asteroids.remove(a)
                    self.bullets.remove(b)

    def distance(self, p1, p2):
        if len(p1) != len(p2):
            print("Parameter length mismatch")
            return None

        result = 0.0

        for i in range(len(p1)):
            result += math.pow(p1[i] - p2[i], 2)

        return math.sqrt(result)
