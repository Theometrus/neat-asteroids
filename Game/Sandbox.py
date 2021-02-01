import itertools
import math
import os
import random

import pygame as pg

from Game.Asteroid import Asteroid
from Game.Bullet import Bullet
from Game.Grid import Grid
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
        self.grid = Grid(RESOLUTION[0], RESOLUTION[1], 128)
        self.grid.insert(self.player, self.player.rect.center[0], self.player.rect.center[1])

    def display(self):
        self.setup_background()

        self.bullets.draw(self.screen)
        self.asteroids.draw(self.screen)
        self.player_group.draw(self.screen)

    def tick(self):
        self.player.wrap_around_screen()

        self.remove_out_of_screen(self.bullets)
        self.remove_out_of_screen(self.asteroids)
        self.replenish_asteroids()

        for i in self.bullets:
            self.update_element_and_grid(i)

        for i in self.asteroids:
            self.update_element_and_grid(i)

        self.update_element_and_grid(self.player)

        self.check_collisions()
        self.propagate_player()
        self.cooldown += 1

    def update_element_and_grid(self, elem):
        old_x = elem.rect.center[0]
        old_y = elem.rect.center[1]
        old_key = self.grid.get_key(old_x, old_y)
        elem.update()
        new_key = self.grid.get_key(elem.rect.center[0], elem.rect.center[1])

        if old_key != new_key:
            self.grid.delete(elem, old_x, old_y)
            self.grid.insert(elem, elem.rect.center[0], elem.rect.center[1])

    def propagate_player(self):
        vision_inputs = {}

        for key, val in self.player.vision.items():
            vision_inputs[key] = 0.0

        for a in self.asteroids:
            for key, val in self.player.vision.items():
                p1, p2 = self.find_line_circle_intersection(a.rect.center[0], a.rect.center[1], a.radius, val[0], val[1])
                point = self.find_closest_of_two_points(p1, p2, self.player.rect.center)

                if point is not None:
                    epsilon = 0.0000001
                    dist = self.distance(self.player.rect.center, point)
                    length = self.distance(val[0], val[1])

                    # Check if this point is on this line segment
                    if -epsilon < (dist + self.distance(point, val[1]) - length) < epsilon:
                        scaled_dist = 1 - (dist / length)  # Want the input to get stronger the closer the enemy is
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
                bullet = Bullet(self.player, self.bullet_img)
                self.bullets.add(bullet)
                self.grid.insert(bullet, bullet.rect.center[0], bullet.rect.center[1])

    def find_closest_of_two_points(self, p1, p2, center):
        if p1 == (None, None) and p2 == (None, None):
            return None
        elif p2 == (None, None):
            return p1

        dist1 = self.distance(center, p1)
        dist2 = self.distance(center, p2)

        return p1 if dist1 < dist2 else p2

    # Courtesy of https://stackoverflow.com/questions/23016676/line-segment-and-circle-intersection
    def find_line_circle_intersection(self, cx, cy, radius, point1,  point2):
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]

        a = dx * dx + dy * dy
        b = 2 * (dx * (point1[0] - cx) + dy * (point1[1] - cy))
        c = (point1[0] - cx) * (point1[0] - cx) + (point1[1] - cy) * (point1[1] - cy) - radius * radius

        det = b * b - 4 * a * c

        if a <= 0.0000001 or det < 0:
            # No real solutions.
            intersection1 = (None, None)
            intersection2 = (None, None)
        elif det == 0:
            # One solution.
            t = -b / (2 * a)
            intersection1 = (point1[0] + t * dx, point1[1] + t * dy)
            intersection2 = (None, None)
        else:
            # Two solutions.
            t = (-b + math.sqrt(det)) / (2 * a)
            intersection1 = (point1[0] + t * dx, point1[1] + t * dy)
            t = (-b - math.sqrt(det)) / (2 * a)
            intersection2 = (point1[0] + t * dx, point1[1] + t * dy)

        return intersection1, intersection2

    def setup_background(self):
        brick_width, brick_height = self.bg.get_width(), self.bg.get_height()
        for x, y in itertools.product(range(0, RESOLUTION[0], brick_width),
                                      range(0, RESOLUTION[1], brick_height)):
            self.screen.blit(self.bg, (x, y))

    def remove_out_of_screen(self, sprites):
        count = 0

        for s in sprites:
            if s.position.x > RESOLUTION[0] + 50 or s.position.x < -50 or s.position.y <= -50 or s.position.y > \
                    RESOLUTION[1] + 50:
                sprites.remove(s)
                self.grid.delete(s, s.rect.center[0], s.rect.center[1])
                count += 1

        return count

    def replenish_asteroids(self):
        while len(self.asteroids) < ASTEROID_COUNT:
            asteroid = Asteroid(random.choice(self.ast_imgs))
            self.asteroids.add(asteroid)
            self.grid.insert(asteroid, asteroid.rect.center[0], asteroid.rect.center[1])

    def check_collisions(self):
        player_zone = self.grid.get_zone(self.player.rect.center[0], self.player.rect.center[1])

        for i in player_zone:
            if i == self.player:
                continue

            if i not in self.bullets and pg.sprite.collide_circle(self.player, i):
                self.player.die()

        for b in self.bullets:
            b_zone = self.grid.get_zone(b.rect.center[0], b.rect.center[1])
            asteroids = [x for x in b_zone if type(x) is Asteroid]
            for i in asteroids:
                if pg.sprite.collide_circle(i, b):
                    self.player.score += 1
                    self.asteroids.remove(i)
                    self.bullets.remove(b)
                    self.grid.delete(i, i.rect.center[0], i.rect.center[1])
                    self.grid.delete(b, b.rect.center[0], b.rect.center[1])


    def distance(self, p1, p2):
        if len(p1) != len(p2):
            print("Parameter length mismatch")
            return None

        result = 0.0

        for i in range(len(p1)):
            result += math.pow(p1[i] - p2[i], 2)

        return math.sqrt(result)
