import pygame as pg

from AsteroidFitnessEvaluator import AsteroidFitnessEvaluator
from Game.Sandbox import Sandbox
from NEAT.classes.Puppeteers.Population import Population
from settings import RESOLUTION


def main():
    screen = pg.display.set_mode(RESOLUTION)
    pg.display.set_caption("NEAT Asteroids")

    delay = 0

    fitness_eval = AsteroidFitnessEvaluator()
    population = Population(fitness_eval)
    gen = 0
    running = True
    while running:
        avg_score = 0.0
        ctr = 0
        print("=========== GENERATION {} START ===========".format(gen))
        for i in population.networks:
            sandbox = Sandbox(screen, i)
            ctr += 1
            print("PLAYER {} of {}".format(ctr, len(population.networks)))
            while not sandbox.player.dead:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False

                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_RIGHT:
                            delay -= 10

                        elif event.key == pg.K_LEFT:
                            delay += 10

                sandbox.tick()
                sandbox.display()
                pg.display.update()
                pg.time.delay(delay)

            fitness_eval.calculate(sandbox.player)

        avg = sum(list(fitness_eval.networks.values())) / len(population.networks)

        print("AVERAGE SCORE: {}".format(avg))
        population.evolve()
        fitness_eval.networks = {}
        print("=========== GENERATION {} END ===========".format(gen))
        gen += 1


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()



