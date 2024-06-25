from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of player, score, and color)
# e.g. if alton == 1 and score41 == 1 and green == 1, then Alton scored 41 points and threw green darts
alton, evan, greg, jeffrey = players = intvar(1, 4, shape=4)
score41, score48, score55, score62 = scores = intvar(1, 4, shape=4)
green, red, white, yellow = colors = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
player_to_int = None  # N/A
score_to_int = {score41: 41, score48: 48, score55: 55, score62: 62}  # in points
color_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def scored_higher_than(var1, var2):
    """
    Formulate the constraint that var1 scored higher than var2.
    """
    return [((s1 == var1) & (s2 == var2)).implies(score_to_int[s1] > score_to_int[s2])
            for s1 in scores for s2 in scores]


def scored_exactly_higher_than(var1, var2, diff):
    """
    Formulate the constraint that var1 scored exactly diff points higher than var2.
    """
    return [((s1 == var1) & (s2 == var2)).implies(score_to_int[s1] == score_to_int[s2] + diff)
            for s1 in scores for s2 in scores]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(players)
m += AllDifferent(scores)
m += AllDifferent(colors)

# Clue 1: Greg threw the red darts:
m += greg == red

# Clue 2: Alton scored 7 points higher than Evan:
m += scored_exactly_higher_than(alton, evan, 7)

# Clue 3: The contestant who threw the yellow darts scored somewhat higher than the player who threw the white darts:
m += scored_higher_than(yellow, white)

# Clue 4: The player who scored 48 points threw the yellow darts:
m += score48 == yellow

# Clue 5: Greg scored 7 points higher than Jeffrey:
m += scored_exactly_higher_than(greg, jeffrey, 7)

