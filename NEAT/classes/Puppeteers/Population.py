import math
import random

from NEAT.classes.Activation.Bias import Bias
from NEAT.classes.Activation.Identity import Identity
from NEAT.classes.Activation.Sigmoid import Sigmoid
from NEAT.classes.Individuals.Genome import Genome
from NEAT.classes.Individuals.Network import Network
from NEAT.classes.Individuals.Node import Node
from NEAT.classes.Individuals.Species import Species
from NEAT.classes.Puppeteers.InnovationGuardian import InnovationGuardian
from NEAT.config.settings import *


class Population:
    def __init__(self, fitness_evaluator):
        # Note: fresh networks are created with no connections whatsoever. Connections must be mutated into
        self.networks = []
        self.species = []
        self.fitness_evaluator = fitness_evaluator
        self.innovation_guard = InnovationGuardian()

        self.initial_nodes = []
        self.make_starting_nodes()  # Template nodes for new networks to copy from
        self.make_starting_networks()  # Initial population members

    def propagate(self, inputs):
        for i in self.networks:
            i.calculate(inputs)

    def evolve(self):
        self.innovation_guard.new_generation()
        self.speciate()
        self.erase_extinct_species()
        self.assign_new_representatives()
        self.calculate_fitnesses()
        self.adjust_species_sizes()
        self.cull()
        self.reproduce()
        self.reset_networks()

    def speciate(self):
        reps = []

        for n in self.networks:
            n.species = None

        # Remove everyone except the rep from species
        for s in self.species:
            s.representative.species = s
            s.members = [s.representative]
            reps.append(s.representative)

        for n in self.networks:
            if n in reps:
                continue

            classified = False

            for s in self.species:
                delta = n.compare_to(s.representative)
                if delta <= DELTA_THRESHOLD:
                    s.members.append(n)
                    n.species = s
                    classified = True
                    break

            if not classified:
                species = Species(n)
                species.members.append(n)
                self.species.append(species)
                n.species = species

    def assign_new_representatives(self):
        for s in self.species:
            s.representative = random.choice(s.members)

    def erase_extinct_species(self):
        # Prevent empty/1-member species lists from cluttering the program

        orphans = []

        for s in self.species:
            if len(s.members) == 1:
                orphans.append(s.members[0])
                rand_species = random.choice([x for x in self.species if x != s and len(x.members) > 0])
                rand_species.members.append(s.members[0])
                s.members[0].species = rand_species
                s.members = []

        self.species = [x for x in self.species if len(x.members) > 1]

    def calculate_fitnesses(self):
        # Calculate the mean adjusted fitnesses based on the specifications described in the original NEAT paper

        for s in self.species:
            s.calculate_fitnesses(self.fitness_evaluator)

    def adjust_species_sizes(self):
        # Make species shrink or grow depending on their performance

        mean_fitness = sum(s.average_fitness for s in self.species) / POPULATION_SIZE

        for s in self.species:
            if mean_fitness == 0:
                s.new_size = len(s.members)
                return
            elif s.stagnation_timer == 0:
                s.new_size = 0
                mean_fitness *= POPULATION_SIZE
                mean_fitness -= s.average_fitness
                mean_fitness /= POPULATION_SIZE
                continue
            s.new_size = round(s.average_fitness / mean_fitness)

    def cull(self):
        # Exterminate the lowest performing members of most species (without causing extinctions)

        for s in self.species:
            s.members.sort(key=lambda x: x.fitness)
            cutoff = math.floor((1 - SURVIVORS) * len(s.members))

            if len(s.members) - cutoff < 5:  # Don't eradicate small species
                continue

            s.members = s.members[cutoff:]

    def reproduce(self):
        # The entire population is replaced by offspring of top performing members

        self.networks = []

        for s in self.species:
            offspring = [s.representative]
            self.networks.append(s.representative)
            elite_num = round(ELITES * len(s.members))
            elite_cutoff = len(s.members) - elite_num

            # Transfer some percentage of the population to the next generation unaltered (elitism)
            for i in s.members[elite_cutoff:]:
                elite_clone = i.get_child(i, self.create_empty_genome())  # Mating a genome with itself clones it
                offspring.append(elite_clone)
                self.networks.append(elite_clone)

            for i in range(s.new_size - 1 - elite_num):  # Excluding the representative and the elites
                # Decide whether to use sexual (crossover) or asexual reproduction (mutation)
                if random.uniform(0.0, 1.0) <= MUTATION_RATE:
                    parent = self.tournament_select(5, s.members)  # Select a best of 5
                    child = parent.get_child(parent, self.create_empty_genome())  # Effectively clones the parent
                    child.mutate()
                else:
                    parent_a = self.tournament_select(5, s.members)
                    parent_b = self.tournament_select(5, [x for x in s.members if x != parent_a])

                    child = parent_a.get_child(parent_b, self.create_empty_genome())

                offspring.append(child)
                self.networks.append(child)
            s.members = offspring

    def reset_networks(self):
        # Any elites that get carried over must be reset

        for i in self.networks:
            i.outputs = []
            i.fitness = 0.0

    def create_empty_genome(self):
        nodes_clone = []

        for node in self.initial_nodes:
            nodes_clone.append(node.clone())

        return Genome(nodes_clone, self.innovation_guard)

    def make_starting_nodes(self):
        for i in range(BIAS_NODES):
            node = Node(self.innovation_guard.node_innov, IN_NODE_X, i, Bias(), "BIAS")
            self.initial_nodes.append(node)
            self.innovation_guard.node_innov += 1

        for i in range(INPUT_NODES):
            node = Node(self.innovation_guard.node_innov, IN_NODE_X, i, Identity(), "SENSOR")
            self.initial_nodes.append(node)
            self.innovation_guard.node_innov += 1

        for i in range(OUTPUT_NODES):
            node = Node(self.innovation_guard.node_innov, OUT_NODE_X, i, Sigmoid(), "OUTPUT")
            self.initial_nodes.append(node)
            self.innovation_guard.node_innov += 1

    def make_starting_networks(self):
        for _ in range(POPULATION_SIZE):
            genome = self.create_empty_genome()
            network = Network(genome)
            self.networks.append(network)

    def tournament_select(self, rounds, contestants):
        champion = None

        for _ in range(rounds):
            challenger = random.choice(contestants)

            if champion is None or challenger.fitness > champion.fitness:
                champion = challenger

        return champion
