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
    sandboxes = [Sandbox(screen, brain) for brain in population.networks]
    first_iteration = True
    print("========== GENERATION {} START ==========".format(gen))
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    delay -= 10

                elif event.key == pg.K_LEFT:
                    delay += 10

        all_dead = True

        for i in sandboxes:
            if not i.player.dead:
                i.tick()
                all_dead = False

        # Display player from the biggest (probably most fit as of last generation) species
        biggest_species = 0.0
        player = None
        if not first_iteration:
            for s in population.species:
                if len(s.members) > biggest_species:
                    biggest_species = len(s.members)
                    player = [x for x in sandboxes if x.player.brain == s.representative][0]
        else:
            player = sandboxes[0]

        # player = sandboxes[0]
        player.display()
        pg.display.update()
        pg.time.delay(delay)

        if all_dead:
            first_iteration = False

            for i in sandboxes:
                fitness_eval.calculate(i.player)

            avg = sum(list(fitness_eval.networks.values())) / len(population.networks)

            print("AVERAGE SCORE: {}".format(avg))
            population.evolve()
            fitness_eval.networks = {}
            print("=========== GENERATION {} END ===========".format(gen))
            gen += 1
            sandboxes = [Sandbox(screen, brain) for brain in population.networks]
            print("========== GENERATION {} START ==========".format(gen))


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
