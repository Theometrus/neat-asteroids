import itertools
import math
import os
import random

import numpy as np
import pygame as pg
import pygame.freetype
from math import atan2, degrees, pi

from Game.Asteroid import Asteroid
from Game.Bullet import Bullet
from Game.Grid import Grid
from Game.NetworkRenderer import NetworkRenderer
from Game.Player import Player
from settings import RESOLUTION, ASTEROID_COUNT


class Sandbox:
    def __init__(self, screen, brain, extra_ast):
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
        self.displaying = False
        self.net_renderer = NetworkRenderer(self.screen)
        self.time = 0
        self.bounty_timer = 20
        self.extra_asteroids = extra_ast

    def display(self):
        self.setup_background()
        if self.player.target == self.player.closest_asteroid:
            pg.draw.line(self.screen, color=(255, 255, 255), start_pos=self.player.rect.center,
                         end_pos=self.player.closest_asteroid.rect.center, width=2)
        else:
            pg.draw.line(self.screen, color=(255, 255, 255), start_pos=self.player.rect.center,
                         end_pos=self.player.closest_asteroid.rect.center)
        pg.draw.line(self.screen, color=(255, 0, 0), start_pos=self.player.rect.center,
                     end_pos=self.player.target.rect.center)

        self.bullets.draw(self.screen)
        self.asteroids.draw(self.screen)
        self.player_group.draw(self.screen)

        ft_font = pygame.freetype.SysFont('Sans', 20)
        text_str = 'Score: {}'.format(self.player.score)
        text_rect = ft_font.get_rect(text_str)
        text_rect.center = self.screen.get_rect().topleft
        ft_font.render_to(self.screen, (text_rect[0] + 50, text_rect[1] + 20), text_str, (255, 255, 255))

        if gints is None:
            return

        text_str = 'Inputs: {}'.format(list(np.around(gints, 2)))
        text_rect = ft_font.get_rect(text_str)
        text_rect.center = self.screen.get_rect().topright
        ft_font.render_to(self.screen, (text_rect[0] - 110, text_rect[1] + 20), text_str, (255, 255, 255))

        text_str = 'Outputs: {}'.format(list(np.around(gouts, 2)))
        text_rect = ft_font.get_rect(text_str)
        text_rect.center = self.screen.get_rect().topright
        ft_font.render_to(self.screen, (text_rect[0] - 100, text_rect[1] + 50), text_str, (255, 255, 255))

        text_str = 'Time: {}'.format(self.bounty_timer)
        text_rect = ft_font.get_rect(text_str)
        text_rect.center = self.screen.get_rect().midtop
        ft_font.render_to(self.screen, (text_rect[0] - 40, text_rect[1] + 20), text_str, (255, 255, 255))

        self.net_renderer.render(self.player.brain)

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
        self.cooldown -= 1
        self.cooldown = max(0, self.cooldown)
        self.time += 1

        if self.time % 60 == 0:
            self.bounty_timer -= 1
            if self.bounty_timer <= 0:
                self.player.die()

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
        ast = random.choice(list(self.asteroids))
        closest = self.distance(ast.rect.center, self.player.rect.center)
        for a in self.asteroids:
            dist = self.distance(self.player.rect.center, a.rect.center)
            if dist < closest:
                closest = dist
                ast = a

        closest = self.norm_distance(self.player, ast)
        self.player.closest_asteroid = ast
        degs = self.norm_angle(ast)

        if self.player.target is None:
            self.player.target = random.choice(list(self.asteroids))

        target_dist = self.norm_distance(self.player.target, self.player)
        target_angle = self.norm_angle(self.player.target)

        inputs = [degs, closest, target_angle, target_dist]
        outputs = self.player.propagate(inputs)

        if self.displaying:
            global gints
            gints = inputs
            global gouts
            gouts = outputs

        # Move
        if outputs[0] >= 0.8:
            self.player.accelerate()

        # Steer
        if outputs[1] >= 0.9:
            if outputs[0] >= 0.9 or outputs[0] <= 0.1:
                self.player.steer(1)
            else:
                self.player.steer(5)
        elif outputs[1] <= 0.1:
            if outputs[0] >= 0.9 or outputs[0] <= 0.1:
                self.player.steer(-1)
            else:
                self.player.steer(-5)

        # Shoot
        if outputs[2] >= 0.8:
            if self.cooldown == 0:  # Don't allow player to make bullet laser beams
                bullet = Bullet(self.player, self.bullet_img)
                self.bullets.add(bullet)
                self.grid.insert(bullet, bullet.rect.center[0], bullet.rect.center[1])
                self.player.shots_fired += 1
                self.cooldown = 50

    def norm_angle(self, a):
        dx = a.rect.center[0] - self.player.rect.center[0]
        dy = a.rect.center[1] - self.player.rect.center[1]
        rads = atan2(-dy, dx)
        rads %= 2 * pi
        degs = degrees(rads)

        degs = abs(360 - self.player.angle - abs(degs))
        if degs > 180:
            degs -= 360
            degs = abs(degs)

        return degs / 180

    def norm_distance(self, a, b):
        target_dist = self.distance(a.rect.center, b.rect.center)
        target_dist /= (self.distance((0, 0), (RESOLUTION[0], 0)) / 2)
        target_dist = max(1 - target_dist, 0.00)
        return target_dist

    def setup_background(self):
        brick_width, brick_height = self.bg.get_width(), self.bg.get_height()
        for x, y in itertools.product(range(0, RESOLUTION[0], brick_width),
                                      range(0, RESOLUTION[1], brick_height)):
            self.screen.blit(self.bg, (x, y))

    def remove_out_of_screen(self, sprites):
        count = 0

        for s in sprites:
            if s.position.x > RESOLUTION[0] + 30 or s.position.x < -50 or s.position.y <= -50 or s.position.y > \
                    RESOLUTION[1] + 50:
                sprites.remove(s)
                self.grid.delete(s, s.rect.center[0], s.rect.center[1])
                count += 1
                if s == self.player.target:
                    self.player.target = None

        return count

    def replenish_asteroids(self):
        while len(self.asteroids) < ASTEROID_COUNT + self.extra_asteroids:
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
                self.player.killed = True

        for b in self.bullets:
            b_zone = self.grid.get_zone(b.rect.center[0], b.rect.center[1])
            asteroids = [x for x in b_zone if type(x) is Asteroid]
            for i in asteroids:
                if pg.sprite.collide_circle(i, b):
                    if self.player.closest_asteroid == i:
                        self.player.score += 1
                        self.player.shots_hit += 1

                    if self.player.target == i:
                        self.player.score += round((self.norm_distance(self.player, self.player.target)) * 5)
                        self.player.shots_hit += 1
                        self.bounty_timer = 20
                        self.player.target = None

                    if self.player.target != i and self.player.closest_asteroid != i:
                        self.player.score -= 1
                        self.player.score = max(self.player.score, 0)

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
