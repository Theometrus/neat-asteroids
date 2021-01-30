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
        self.player_img = pg.image.load(os.path.join(img_folder, 'player.png'))
        self.bg = pg.image.load(os.path.join(img_folder, 'Space_Stars4.png'))
        self.bullet_img = pg.image.load(os.path.join(img_folder, 'bullet.png'))

        self.ast_imgs = [pg.image.load(os.path.join(img_folder, 'ast1.png')),
                         pg.image.load(os.path.join(img_folder, 'ast2.png')),
                         pg.image.load(os.path.join(img_folder, 'ast3.png')),
                         pg.image.load(os.path.join(img_folder, 'ast4.png'))]

        self.player = Player(300, 200, self.player_img)
        self.screen = screen
        self.sprites = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.sprites.add(self.player)
        self.asteroid_count = 0

    def display(self):
        self.setup_background()

        self.sprites.draw(self.screen)
        self.asteroids.draw(self.screen)

    def tick(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            bullet = Bullet(self.player, self.bullet_img)
            self.sprites.add(bullet)

        self.player.wrap_around_screen()

        self.remove_out_of_screen(self.sprites)
        removed = self.remove_out_of_screen(self.asteroids)
        self.asteroid_count -= removed

        self.sprites.update()
        self.asteroids.update()
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
        while self.asteroid_count < ASTEROID_COUNT:
            self.asteroids.add(Asteroid(random.choice(self.ast_imgs)))
            self.asteroid_count += 1
