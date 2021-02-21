import math
import random

import pygame as pg

from AsteroidFitnessEvaluator import AsteroidFitnessEvaluator
from Game.Sandbox import Sandbox
from NEAT.classes.Puppeteers.Population import Population
from settings import RESOLUTION, ASTEROID_COUNT


def main():
    screen = pg.display.set_mode([RESOLUTION[0] * 2, RESOLUTION[1]])
    pg.display.set_caption("NEAT Asteroids")

    delay = 0

    fitness_eval = AsteroidFitnessEvaluator()
    population = Population(fitness_eval)
    gen = 0
    running = True
    sandboxes = [Sandbox(screen, brain, 0) for brain in population.networks]
    print("========== GENERATION {} START ==========".format(gen))
    player = random.choice(sandboxes)
    player.displaying = True
    clock = pg.time.Clock()
    speed_run = False
    while running:
        screen.fill((0, 0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    delay -= 10

                elif event.key == pg.K_LEFT:
                    delay += 10

                elif event.key == pg.K_n:
                    player.displaying = False
                    living_players = [x for x in sandboxes if not x.player.dead]
                    player = random.choice(living_players)
                    player.displaying = True

                elif event.key == pg.K_s:
                    speed_run = not speed_run

        all_dead = True

        for i in sandboxes:
            if not i.player.dead:
                i.tick()
                all_dead = False

        if player.player.dead:
            living_players = [x for x in sandboxes if not x.player.dead]
            if len(living_players) > 0:
                player = random.choice(living_players)
                player.displaying = True

        player.display()
        pg.display.update()
        pg.time.delay(delay)
        pg.display.set_caption(
            "NEAT Asteroids - {} Player(s) Surviving".format(len([x for x in sandboxes if not x.player.dead])))

        if not speed_run:
            clock.tick(60)

        if all_dead:
            for i in sandboxes:
                fitness_eval.calculate(i.player)

            avg = sum(list(fitness_eval.networks.values())) / len(population.networks)

            print("AVERAGE FITNESS: {}".format(avg))
            population.evolve()
            fitness_eval.networks = {}
            print("=========== GENERATION {} END ===========".format(gen))
            gen += 1
            ast = ASTEROID_COUNT
            # ast = min(math.floor(round(gen / 10)), 15)  # Cap asteroids at 15
            sandboxes = [Sandbox(screen, brain, ast) for brain
                         in population.networks]
            print("========== GENERATION {} START ==========".format(gen))
            print("THIS GENERATION HAS {} ASTEROIDS".format(ASTEROID_COUNT))
            player = random.choice(sandboxes)
            player.displaying = True
            print("NUMBER OF SPECIES: {}".format(len(population.species)))


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()

