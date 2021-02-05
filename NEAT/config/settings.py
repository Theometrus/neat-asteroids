# =========================== Mutation properties ============================ #
CLONE_RATE = 0.25  # Portion of individuals to go into the next generation unaltered

NO_MUTATION = 0.15
MUT_ADD_LINK = 0.05
MUT_ADD_NODE = 0.01
MUT_CHANGE_ACTIVATION = 0.01
MUT_TOGGLE_LINK = 0.001
MUT_REMOVE_LINK = 0.001
MUT_REMOVE_NODE = 0.0001
MUT_WEIGHT_ADJUST = 0.8  # Controls overall how likely the next two mutation types are to occur per connection

MUT_WEIGHT_SHIFT = 0.7
MUT_WEIGHT_REASSIGN = 0.1

# ============================ Network topology ============================= #
FULLY_CONNECTED = False  # Whether or not the networks start out with all initial connections, or none

INPUT_NODES = 3
OUTPUT_NODES = 3

WEIGHT_INITIAL_CAP = 1.0
WEIGHT_PERTURBATION = 0.04

# ========================== Population parameters ========================== #
POPULATION_SIZE = 300
EXCESS_COEFFICIENT = 3.0
DISJOINT_COEFFICIENT = 3.0
WEIGHT_COEFFICIENT = 1.0
DELTA_THRESHOLD = 3.0
SURVIVORS = 0.2
ELITISM = True

# ============================== DO NOT MODIFY ============================== #
IN_NODE_X = 0.1
OUT_NODE_X = 0.9
