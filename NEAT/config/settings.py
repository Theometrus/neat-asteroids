# =========================== Mutation properties ============================ #
MUTATION_RATE = 0.35  # Portion of individuals to reproduce asexually through mutation

# Once an individual is chosen to mutate, they will mutate up to this many times, choosing
# from the mutations below (and respecting the assigned probabilities)
MUTATIONS_AT_ONCE = 5

MUT_ADD_LINK = 0.18
MUT_ADD_NODE = 0.01
MUT_TOGGLE_LINK = 0.01
MUT_REMOVE_LINK = 0.01
MUT_REMOVE_NODE = 0.001

MUT_WEIGHT_ADJUST = 0.8  # Controls overall how likely the next two mutation types are to occur per connection
MUT_WEIGHT_SHIFT = 0.6
MUT_WEIGHT_REASSIGN = 0.1

# ============================ Network topology ============================= #
INPUT_NODES = 9
OUTPUT_NODES = 5
BIAS_NODES = 1  # Recommended to leave this unchanged

WEIGHT_INITIAL_CAP = 170.0
WEIGHT_PERTURBATION = 15.0

# ========================== Population parameters ========================== #
POPULATION_SIZE = 50
EXCESS_COEFFICIENT = 2.0
DISJOINT_COEFFICIENT = 2.0
WEIGHT_COEFFICIENT = 1.0
DELTA_THRESHOLD = 2.5
SURVIVORS = 0.2
ELITES = 0.1

# ========================= General configurations ========================== #
RESOLUTION = [720, 480]
BG_COLOR = 247, 235, 203

# ============================== DO NOT MODIFY ============================== #
IN_NODE_X = 0.1
OUT_NODE_X = 0.9
