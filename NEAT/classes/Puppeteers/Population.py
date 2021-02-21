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
        self.networks = []
        self.species = []
        self.fitness_evaluator = fitness_evaluator
        self.innovation_guard = InnovationGuardian()

        self.initial_nodes = []
        self.make_starting_nodes()  # Template nodes for new networks to copy from
        self.make_starting_networks()  # Initial population members

        if FULLY_CONNECTED:
            self.connect_networks()

        # Randomize initial children to kickstart the algo
        for i in self.networks:
            i.mutate()

    def connect_networks(self):
        for n in self.networks:
            for _ in range((INPUT_NODES + 1) * OUTPUT_NODES):
                n.genome.mutate_add_link()

    def propagate(self, inputs):
        for i in self.networks:
            i.calculate(inputs)

    def evolve(self):
        self.innovation_guard.new_generation()
        self.speciate()
        self.erase_extinct_species()
        self.calculate_initial_fitnesses()
        self.cull()
        self.adjust_fitnesses()
        self.adjust_species_sizes()
        self.reproduce()
        self.assign_new_representatives()

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
                species.representative = n
                n.species = species

    def assign_new_representatives(self):
        for s in self.species:
            # s.representative = s.champion
            s.representative = random.choice(s.members)

    def erase_extinct_species(self):
        self.species.sort(key=lambda x: x.current_best)

        new_species = [x for x in self.species if len(x.members) > 0 and x.stagnation_timer > 0]

        # If the whole population has not improved in the last couple of generations, only allow the top two species
        # to reproduce to refocus the search into the most promising areas
        if len(new_species) == 0:
            new_species = self.species[-2:]

        self.species = new_species

    def calculate_initial_fitnesses(self):
        for s in self.species:
            s.calculate_fitnesses(self.fitness_evaluator)

    def adjust_fitnesses(self):
        # Calculate the mean adjusted fitnesses based on the specifications described in the original NEAT paper

        for s in self.species:
            s.adjust_fitnesses()

    def adjust_species_sizes(self):
        # Make species shrink or grow depending on their performance

        mean_fitness_sum = sum(s.average_fitness for s in self.species)

        for s in self.species:
            if mean_fitness_sum == 0:
                s.new_size = len(s.members)
                print("Error: mean fitness was zero!")
                return

            s.new_size = math.floor(s.average_fitness / mean_fitness_sum * POPULATION_SIZE)

    def cull(self):
        # Exterminate the lowest performing members of most species (without causing extinctions)

        for s in self.species:
            s.members.remove(s.representative)
            s.members.sort(key=lambda x: x.fitness)
            cutoff = math.floor((1 - SURVIVORS) * len(s.members))

            if len(s.members) - cutoff < 2:  # Don't eradicate small species
                s.members.append(s.representative)
                continue

            s.members = s.members[cutoff:]
            s.members.append(s.representative)

    def reproduce(self):
        # The entire population is replaced by offspring of top performing members

        self.networks = []
        self.species = [x for x in self.species if x.new_size > 0]
        elites = 0

        for s in self.species:
            # Mating a genome with itself clones it
            rep_clone = s.representative.get_child(s.representative, self.create_empty_genome())
            offspring = [rep_clone]
            rep_clone.species = s
            s.representative = rep_clone
            self.networks.append(rep_clone)

            # Transfer the best member of the species to the next generation unaltered
            if ELITISM:
                elite_child = s.champion.get_child(s.champion, self.create_empty_genome())
                elite_child.species = s
                offspring.append(elite_child)
                self.networks.append(elite_child)
                elites = 1

            for i in range(s.new_size - 1 - elites):  # Excluding the representative and the elite (if enabled)
                if random.uniform(0.0, 1.0) <= CLONE_RATE:
                    parent = self.tournament_select(5, s.members)  # Select a best of 5
                    child = parent.get_child(parent, self.create_empty_genome())  # Effectively clones the parent
                else:
                    parent_a = self.tournament_select(5, s.members)
                    parent_b = self.tournament_select(5, s.members)

                    child = parent_a.get_child(parent_b, self.create_empty_genome())
                    child.mutate()

                offspring.append(child)
                self.networks.append(child)
            s.members = offspring

        # If due to flooring we didn't get enough networks, add members to the best species
        if len(self.networks) < POPULATION_SIZE:
            self.species.sort(key=lambda x: x.current_best)
            species = self.species[-1]

            for _ in range(POPULATION_SIZE - len(self.networks)):
                parent_a = self.tournament_select(5, species.members)
                parent_b = self.tournament_select(5, species.members)

                child = parent_a.get_child(parent_b, self.create_empty_genome())
                child.mutate()
                child.species = species
                species.members.append(child)
                self.networks.append(child)

    def create_empty_genome(self):
        nodes_clone = []

        for node in self.initial_nodes:
            nodes_clone.append(node.clone())

        return Genome(nodes_clone, self.innovation_guard)

    def make_starting_nodes(self):
        node = Node(self.innovation_guard.node_innov, IN_NODE_X, 0, Bias(), "BIAS")
        self.initial_nodes.append(node)
        self.innovation_guard.node_innov += 1

        for i in range(INPUT_NODES):
            node = Node(self.innovation_guard.node_innov, IN_NODE_X, i + 1, Identity(), "SENSOR")
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
