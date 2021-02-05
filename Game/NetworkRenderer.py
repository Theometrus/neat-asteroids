from pygame import gfxdraw
import pygame as pg

from settings import RESOLUTION


class NetworkRenderer:
    def __init__(self, screen):
        self.screen = screen

    def render(self, network):
        pg.draw.rect(self.screen, (30, 30, 30), (RESOLUTION[0], 0, 60, RESOLUTION[1]))
        pg.draw.rect(self.screen, (0, 0, 0), (RESOLUTION[0] + 10, 0, 40, RESOLUTION[1]))

        for i in network.genome.connections:
            intensity = min(abs(175 * i.weight) + abs(60 * i.from_node.output) + 15, 255)
            color = (0, 0, 0) if not i.is_enabled else (0, intensity, 0) if i.weight > 0 else (intensity, 0, 0)
            if i.is_enabled:
                pg.draw.line(color=color, width=2, start_pos=(i.from_node.x * (RESOLUTION[0] - 40) + RESOLUTION[0] + 65, i.from_node.y * 60 + 150),
                             end_pos=(i.to_node.x * (RESOLUTION[0] - 40) + RESOLUTION[0] + 35, i.to_node.y * 60 + 150), surface=self.screen)

        for i in network.genome.nodes:
            intensity = min(abs(245 * i.output) + 10, 255)
            x = i.x * (RESOLUTION[0] - 40) + RESOLUTION[0] + 50
            gfxdraw.aacircle(self.screen, round(x), round(i.y * 60 + 150), 17, (0, 0, 0))
            gfxdraw.filled_circle(self.screen, round(x), round(i.y * 60 + 150), 17, (0, 0, intensity))
            font = pg.font.SysFont('comicsans', 20)
            text = font.render(str(i.innovation_number), 1, (255, 255, 255))
            self.screen.blit(text, ((x - 2), i.y * 60 + 145))

        self.render_action(network.genome.nodes[-3], "BOOST", 434, 120, False)

        if network.genome.nodes[-2].output >= 0.8:
            intensity = (255, 255, 255)
            action = "RIGHT"
        elif network.genome.nodes[-2].output <= 0.2:
            intensity = (255, 255, 255)
            action = "LEFT"
        else:
            intensity = (0, 0, 0)
            action = ""

        ft_font = pg.freetype.SysFont('Sans', 10)
        text_str = action
        text_rect = ft_font.get_rect(text_str)
        text_rect.center = (RESOLUTION[0] + 434, 185)
        ft_font.render_to(self.screen, text_rect.center, text_str, intensity)

        self.render_action(network.genome.nodes[-1], "SHOOT", 434, 245, False)
        self.render_action(None, "BIAS", 87, 120, True)
        self.render_action(None, "AST. ANGLE", 72, 185, True)
        self.render_action(None, "AST. DIST.", 77, 245, True)
        self.render_action(None, "BEARING", 77, 305, True)

    def render_action(self, node, action, x_offset, y_offset, always_on):
        if not always_on:
            intensity = (255, 255, 255) if node.output >= 0.8 else (0, 0, 0)
        else:
            intensity = (255, 255, 255)

        ft_font = pg.freetype.SysFont('Sans', 10)
        text_str = action
        text_rect = ft_font.get_rect(text_str)
        text_rect.center = (RESOLUTION[0] + x_offset, y_offset)
        ft_font.render_to(self.screen, text_rect.center, text_str, intensity)



