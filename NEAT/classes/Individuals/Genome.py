import random

import numpy as np

from NEAT.classes.Activation.ReLU import ReLU
from NEAT.classes.Individuals.Connection import Connection
from NEAT.classes.Individuals.Node import Node
from NEAT.config.settings import *


class Genome:
    def __init__(self, nodes, innovation_guardian):
        self.nodes = nodes  # Note: Must be sorted by X value for more efficient computation in the future
        self.connections = []  # Note: Must be sorted by innovation number for faster comparisons
        self.connection_dict = {}  # Used for quickly checking if a given connection already exists in this genome
        self.innovation_guardian = innovation_guardian  # Singleton

    def find_enabled_connection(self):
        found = False
        conn = None

        # Will try to find a connection before timing out
        for i in range(100):
            conn = random.choice(self.connections)
            if not conn.is_enabled:
                continue

            found = True
            break

        if not found:
            return None

        return conn

    def mutate(self):
        # Picks from a choice of mutations according to probabilities specified in settings.py. Does this a given number
        # of times once again based on settings

        values = [MUT_ADD_NODE, MUT_ADD_LINK, MUT_WEIGHT_ADJUST, MUT_TOGGLE_LINK, MUT_REMOVE_LINK, MUT_REMOVE_NODE,
                  NO_MUTATION]

        probabilities = list(map(lambda x: x/sum(values), values))
        choices = [0, 1, 2, 3, 4, 5, 6]

        choice = np.random.choice(choices, 1, p=probabilities)

        if choice == 0:
            self.mutate_add_node()

        elif choice == 1:
            self.mutate_add_link()

        elif choice == 2:
            self.mutate_adjust_weights()

        elif choice == 3:
            self.mutate_toggle_link()

        elif choice == 4:
            self.mutate_remove_connection()

        elif choice == 5:
            self.mutate_remove_node()

        # If choice == 6 do nothing

    def mutate_remove_node(self):
        node = None
        found = False

        for _ in range(100):
            node = random.choice(self.nodes)

            if IN_NODE_X < node.x < OUT_NODE_X:
                found = True
                break

        if not found:
            return

        for c in node.in_links:
            c.from_node.out_links.remove(c)

        for c in node.out_links:
            c.to_node.in_links.remove(c)

        self.nodes.remove(node)
        self.connections = [x for x in self.connections if x not in node.in_links + node.out_links]

    def mutate_remove_connection(self):
        conn = None
        found = False

        if not self.connections:
            return

        # Disallow removal of connections that would leave nodes disconnected and useless
        for _ in range(100):
            conn = random.choice(self.connections)
            if len(conn.from_node.out_links) > 1 and len(conn.to_node.in_links) > 1:
                found = True
                break

        if not found:
            return

        self.connections.remove(conn)
        self.connection_dict.pop((conn.from_node.innovation_number, conn.to_node.innovation_number))

    def mutate_adjust_weights(self):
        # Iterates through all connections and either perturbs the weight slightly or reassigns it completely

        for i in self.connections:
            if random.uniform(0.0, 1.0) <= MUT_WEIGHT_SHIFT + MUT_WEIGHT_REASSIGN:
                if random.uniform(0.0, MUT_WEIGHT_SHIFT + MUT_WEIGHT_REASSIGN) <= MUT_WEIGHT_SHIFT:
                    i.weight += random.uniform(-WEIGHT_PERTURBATION, WEIGHT_PERTURBATION)
                else:
                    i.weight = random.uniform(-WEIGHT_INITIAL_CAP, WEIGHT_INITIAL_CAP)
            else:
                continue

    def mutate_add_node(self):
        if len(self.connections) == 0:
            self.mutate_add_link()
            return

        conn = self.find_enabled_connection()  # Prevent nodes from being formed on disabled connections

        if conn is None:
            return

        conn.is_enabled = False
        x = (conn.to_node.x + conn.from_node.x) / 2  # X coordinate is used for drawing and calculation ordering
        y = ((conn.to_node.y + conn.from_node.y) / 2) * random.uniform(0.5, 1.5)  # Perturb the Y for better drawing

        node = Node(self.innovation_guardian.register_node(conn.from_node.innovation_number,
                                                           conn.to_node.innovation_number), x, y, ReLU(), "HIDDEN")

        conn_a = Connection(conn.from_node, node,
                            self.innovation_guardian.register_connection(conn.from_node.innovation_number,
                                                                         node.innovation_number))

        conn_b = Connection(node, conn.to_node,
                            self.innovation_guardian.register_connection(node.innovation_number,
                                                                         conn.to_node.innovation_number))

        conn_a.weight = 1.0
        conn_b.weight = conn.weight

        node.in_links.append(conn_a)
        node.out_links.append(conn_b)

        conn.from_node.out_links.append(conn_a)
        conn.to_node.in_links.append(conn_b)

        self.insert_connection(conn_a)
        self.insert_connection(conn_b)

        # Insert the new node into this genome in a sorted fashion, for faster computation in the future
        for idx, n in enumerate(self.nodes):
            if n.x <= node.x <= self.nodes[idx + 1].x:
                self.nodes.insert(idx + 1, node)
                break

    def mutate_add_link(self):
        node_a = None
        node_b = None
        found = False

        # Keep trying to find two nodes without a connection between them
        for i in range(100):
            node_a = random.choice(self.nodes)
            node_b = random.choice(self.nodes)

            # Do not pick the same node, nodes in the same category (outputs/inputs/biases), or nodes which are already
            # connected
            if node_a == node_b \
                    or self.connection_dict.get((node_a.innovation_number, node_b.innovation_number)) is not None \
                    or self.connection_dict.get((node_b.innovation_number, node_a.innovation_number)) is not None \
                    or node_a.x == node_b.x:
                continue

            found = True
            break

        if not found:
            return

        # Connections are only created from a lower to a higher X to prevent cycles and assist in calculation sequencing
        if node_a.x > node_b.x:
            node_a, node_b = node_b, node_a

        conn = Connection(node_a, node_b, self.innovation_guardian.register_connection(node_a.innovation_number,
                                                                                       node_b.innovation_number))

        conn.weight = random.uniform(-WEIGHT_INITIAL_CAP, WEIGHT_INITIAL_CAP)

        self.insert_connection(conn)
        node_a.out_links.append(conn)
        node_b.in_links.append(conn)

    def insert_connection(self, conn):
        # Ensures connections are inserted in a sorted order (by innovation). This is done to make crossover
        # faster and simpler down the line

        if len(self.connections) == 0:
            self.connections.append(conn)
            self.connection_dict[(conn.from_node.innovation_number, conn.to_node.innovation_number)] = conn
            return

        for idx, c in enumerate(self.connections):
            if idx + 1 >= len(self.connections):
                self.connections.append(conn)
                break

            if c.innovation_number <= conn.innovation_number <= self.connections[idx + 1].innovation_number:
                self.connections.insert(idx + 1, conn)
                break

        self.connection_dict[(conn.from_node.innovation_number, conn.to_node.innovation_number)] = conn

    def mutate_toggle_link(self):
        # Randomly turns a connection on or off

        if len(self.connections) == 0:
            return

        conn = random.choice(self.connections)

        if conn is not None:
            conn.is_enabled = not conn.is_enabled

    def compare_to(self, genome):
        # Figures out the distance (delta as specified in the paper) between two genomes. Necessary for speciation

        idx_a = 0
        idx_b = 0
        disjoint = 0
        similar = 0
        weight_diff = 0.0

        '''
        The idea here is as such: keep a positional tracker for both genomes. During comparison, move through 
        the genomes in a similar fashion as one would do when performing the merge-sort merge step.  
        '''
        while idx_a < len(self.connections) and idx_b < len(genome.connections):
            innov_a = self.connections[idx_a].innovation_number
            innov_b = genome.connections[idx_b].innovation_number

            if innov_a == innov_b:
                weight_diff += abs(self.connections[idx_a].weight - genome.connections[idx_b].weight)
                similar += 1
                idx_a += 1
                idx_b += 1

            elif innov_a < innov_b:
                disjoint += 1
                idx_a += 1

            else:
                disjoint += 1
                idx_b += 1

        if similar == 0:  # Edge case protection
            weight_diff = 0
        else:
            weight_diff /= similar

        excess = abs(len(self.connections) - len(genome.connections))
        length = max(len(self.connections), len(genome.connections))

        if length == 0:
            delta = 0
        else:
            length = 1 if length < 20 else length  # Encourage speciation in smaller genotypes

            delta = (EXCESS_COEFFICIENT * excess / length) + (
                    DISJOINT_COEFFICIENT * disjoint / length) + WEIGHT_COEFFICIENT * weight_diff

        return delta

    def get_child(self, partner, template):
        """
        Gets the offspring of this genome and the partner. This function assumes that the partner has a lower fitness
        than this genome, which must be kept in mind when using it
        """

        idx_a = 0
        idx_b = 0
        nodes = template.nodes
        node_dict = {}  # Keep track of existing nodes
        connections = []
        connection_dict = {}  # Keep track of existing connections

        # Register existing nodes from the template (bias, sensors and output nodes)
        for n in template.nodes:
            node_dict[n.innovation_number] = n

        while idx_a < len(self.connections) or idx_b < len(partner.connections):
            # B is initially set to infinity to control the flow of the loop down the line
            innov_b = float('inf')

            if idx_a < len(self.connections):
                innov_a = self.connections[idx_a].innovation_number

            # Since the partner has a lower fitness, we don't want the offspring to inherit their excess genes
            else:
                break

            is_enabled = self.connections[idx_a].is_enabled  # Default to the status of the more fit gene

            if idx_b < len(partner.connections):
                innov_b = partner.connections[idx_b].innovation_number

            if innov_a == innov_b:
                if random.uniform(0.0, 1.0) <= 0.5:  # Decide which parent's genes to inherit using a coin flip
                    connection = self.connections[idx_a]

                else:
                    connection = partner.connections[idx_b]

                # 75% chance for a connection to be disabled if it was disabled in either parent
                if self.connections[idx_a].is_enabled != partner.connections[idx_b].is_enabled:
                    if random.uniform(0.0, 1.0) <= 0.75:
                        is_enabled = False
                    else:
                        is_enabled = True
                elif not self.connections[idx_a].is_enabled:
                    is_enabled = False

                idx_a += 1
                idx_b += 1

            elif innov_a < innov_b:
                connection = self.connections[idx_a]
                idx_a += 1

            else:  # Disjoint genes of the partner are not inherited (assuming the partner has lower fitness)
                idx_b += 1
                continue

            from_node: Node = connection.from_node
            to_node: Node = connection.to_node
            weight = connection.weight

            if node_dict.get(from_node.innovation_number) is None:
                node_dict[from_node.innovation_number] = from_node.clone()
                nodes.append(node_dict[from_node.innovation_number])

            if node_dict.get(to_node.innovation_number) is None:
                node_dict[to_node.innovation_number] = to_node.clone()
                nodes.append(node_dict[to_node.innovation_number])

            from_node = node_dict[from_node.innovation_number]
            to_node = node_dict[to_node.innovation_number]

            conn = Connection(from_node, to_node, connection.innovation_number)
            conn.weight = weight
            conn.is_enabled = is_enabled

            connection_dict[(from_node.innovation_number, to_node.innovation_number)] = conn
            connections.append(conn)

            from_node.out_links.append(conn)
            to_node.in_links.append(conn)

        connections = sorted(connections, key=lambda x: x.innovation_number)
        nodes = sorted(nodes, key=lambda x: x.x)

        template.nodes = nodes
        template.connections = connections
        template.connection_dict = connection_dict

        return template
