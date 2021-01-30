import pygame as pg

vec = pg.math.Vector2


class Bullet(pg.sprite.Sprite):
    def __init__(self, player, img):
        pg.sprite.Sprite.__init__(self)
        self.vel = vec(player.acceleration[0] * 15, player.acceleration[1] * 15)
        self.image = pg.transform.rotozoom(img, -player.angle, 1)
        self.rect = self.image.get_rect(center=player.position)
        self.position = vec(player.position)

    def update(self):
        self.position += self.vel
        self.rect.center = self.position


