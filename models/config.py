# config.py

# Simulation parameters
NUM_AGENTS = 50         # Number of country agents
NUM_STEPS = 100         # Number of simulation time steps

# Tie formation parameters
BASE_TIE_FORMATION_PROB = 0.1   # Base probability for tie formation
REGION_FACTOR_SAME = 1.5        # Multiplier if two agents are in the same region
REGION_FACTOR_DIFFERENT = 1.0   # Multiplier if agents are in different regions

# Tie maintenance parameters
TIE_MAINTENANCE_PROB = 0.9  # Constant probability to maintain an existing tie

# Diplomatic priority range
MIN_DIPLOMATIC_PRIORITY = 0.0
MAX_DIPLOMATIC_PRIORITY = 1.0

# Regions available for assignment
REGIONS = ["Europe", "Asia", "Africa", "Americas", "Oceania"]
