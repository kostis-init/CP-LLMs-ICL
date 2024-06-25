from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of ranking, team, and color)
# e.g. if color_blinds == 1 and first == 1 and blue == 1, then Color Blinds finished first and are the blue team
color_blinds, splat_squad, spray_paints, target_bombs = teams = intvar(1, 4, shape=4)
first, second, third, fourth = rankings = intvar(1, 4, shape=4)
blue, orange, white, yellow = colors = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
team_to_int = None  # N/A
ranking_to_int = {first: 1, second: 2, third: 3, fourth: 4}  # in ranking order
color_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def ranked_exactly_behind(var1, var2, diff):
    """
    Formulate the constraint that var1 was ranked diff places behind var2.
    """
    return [((r1 == var1) & (r2 == var2)).implies(ranking_to_int[r1] == ranking_to_int[r2] + diff)
            for r1 in rankings for r2 in rankings]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(teams)
m += AllDifferent(rankings)
m += AllDifferent(colors)

# Clue 1: The Splat Squad was ranked 1 place behind the blue team:
m += ranked_exactly_behind(splat_squad, blue, 1)

# Clue 2: Of the Spray Paints and the white team, one finished first and the other finished fourth:
m += Xor([
    (spray_paints == first) & (white == fourth),
    (spray_paints == fourth) & (white == first)
])

# Clue 3: The orange team is either the Color Blinds or the Target Bombs:
m += Xor([
    orange == color_blinds,
    orange == target_bombs
])

# Clue 4: The blue team was ranked 1 place behind the Target Bombs:
m += ranked_exactly_behind(blue, target_bombs, 1)
