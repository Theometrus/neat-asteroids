# =========================== Mutation properties ============================ #
MUTATION_RATE = 0.35  # Portion of individuals to reproduce asexually through mutation

# Once an individual is chosen to mutate, they will mutate up to this many times, choosing
# from the mutations below (and respecting the assigned probabilities)
MUTATIONS_AT_ONCE = 2

MUT_ADD_LINK = 0.20
MUT_ADD_NODE = 0.08
MUT_TOGGLE_LINK = 0.01
MUT_REMOVE_LINK = 0.01
MUT_REMOVE_NODE = 0.001

MUT_WEIGHT_ADJUST = 0.9  # Controls overall how likely the next two mutation types are to occur per connection
MUT_WEIGHT_SHIFT = 0.7
MUT_WEIGHT_REASSIGN = 0.1

# ============================ Network topology ============================= #
INPUT_NODES = 3
OUTPUT_NODES = 5
BIAS_NODES = 1  # Recommended to leave this unchanged

WEIGHT_INITIAL_CAP = 1.0
WEIGHT_PERTURBATION = 0.02

# ========================== Population parameters ========================== #
POPULATION_SIZE = 150
EXCESS_COEFFICIENT = 3.0
DISJOINT_COEFFICIENT = 3.0
WEIGHT_COEFFICIENT = 1.0
DELTA_THRESHOLD = 3.0
SURVIVORS = 0.2
ELITES = 0

# ============================== DO NOT MODIFY ============================== #
IN_NODE_X = 0.1
OUT_NODE_X = 0.9
