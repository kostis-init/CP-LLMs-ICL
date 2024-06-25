from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of player, year, and position)
# e.g. if awad == 1 and year1976 == 1 and center_back == 1, then Awad started in 1976 as a center back
awad, daregh, gardelli, rothvum = players = intvar(1, 4, shape=4)
year1976, year1979, year1982, year1985 = years = intvar(1, 4, shape=4)
center_back, center_forward, goalie, sweeper = positions = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
player_to_int = None  # N/A
year_to_int = {year1976: 1976, year1979: 1979, year1982: 1982, year1985: 1985}  # in years
position_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def started_before_than(var1, var2, diff):
    """
    Formulate the constraint that var1 started diff years before var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] == year_to_int[y2] - diff)
            for y1 in years for y2 in years]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(players)
m += AllDifferent(years)
m += AllDifferent(positions)

# Clue 1: Daregh started 6 years before the goalie:
m += started_before_than(daregh, goalie, 6)

# Clue 2: The player who started in 1982 was either the goalie or Daregh:
m += Xor([
    year1982 == goalie,
    year1982 == daregh
])

# Clue 3: Awad began playing in 1985:
m += awad == year1985

# Clue 4: The player who started in 1976 was the sweeper:
m += year1976 == sweeper

# Clue 5: Gardelli was either the center back or the player who started in 1979:
m += Xor([
    gardelli == center_back,
    gardelli == year1979
])

