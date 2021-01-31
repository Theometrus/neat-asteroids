import itertools
import os
import random

import pygame as pg

from Game.Asteroid import Asteroid
from Game.Bullet import Bullet
from Game.Player import Player
from settings import RESOLUTION, ASTEROID_COUNT


class Sandbox:
    def __init__(self, screen):
        game_folder = os.path.dirname(__file__)
        img_folder = os.path.join(game_folder, 'sprites')

        self.bg = pg.image.load(os.path.join(img_folder, 'Space_Stars4.png'))
        self.bullet_img = pg.image.load(os.path.join(img_folder, 'bullet.png'))

        self.ast_imgs = [pg.image.load(os.path.join(img_folder, 'ast1.png'))]

        # ,
        # pg.image.load(os.path.join(img_folder, 'ast2.png')),
        # pg.image.load(os.path.join(img_folder, 'ast3.png')),
        # pg.image.load(os.path.join(img_folder, 'ast4.png'))

        self.player_img = pg.image.load(os.path.join(img_folder, 'tile010.png'))

        self.player = Player(300, 200, self.player_img)
        self.screen = screen
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.player_group.add(self.player)

    def display(self):
        self.setup_background()

        self.bullets.draw(self.screen)
        self.asteroids.draw(self.screen)
        self.player_group.draw(self.screen)

    def tick(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            bullet = Bullet(self.player, self.bullet_img)
            self.bullets.add(bullet)

        self.player.wrap_around_screen()

        self.remove_out_of_screen(self.bullets)
        self.remove_out_of_screen(self.asteroids)

        self.bullets.update()
        self.asteroids.update()
        self.player.update()
        self.check_collisions()
        self.replenish_asteroids()

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
