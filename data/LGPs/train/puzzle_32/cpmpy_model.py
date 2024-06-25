from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of ranking, team, and color)
# e.g. if color_blinds == 1 and first == 1 and green == 1, then Color Blinds finished first and uses green paintballs
color_blinds, night_ninjas, oil_crew, target_bombs = teams = intvar(1, 4, shape=4)
first, second, third, fourth = rankings = intvar(1, 4, shape=4)
green, orange, purple, white = colors = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
team_to_int = None  # N/A
ranking_to_int = {first: 1, second: 2, third: 3, fourth: 4}  # in ranking order
color_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def ranked_ahead_of(var1, var2, diff):
    """
    Formulate the constraint that var1 is ranked diff places ahead of var2.
    """
    return [((r1 == var1) & (r2 == var2)).implies(ranking_to_int[r1] == ranking_to_int[r2] - diff)
            for r1 in rankings for r2 in rankings]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(teams)
m += AllDifferent(rankings)
m += AllDifferent(colors)

# Clue 1: The Color Blinds finished first:
m += color_blinds == first

# Clue 2: The Color Blinds was ranked 1 place ahead of the green team:
m += ranked_ahead_of(color_blinds, green, 1)

# Clue 3: The Target Bombs uses white paintballs:
m += target_bombs == white

# Clue 4: Of the Oil Crew and the orange team, one finished third and the other finished second:
m += Xor([
    (oil_crew == third) & (orange == second),
    (oil_crew == second) & (orange == third)
])

