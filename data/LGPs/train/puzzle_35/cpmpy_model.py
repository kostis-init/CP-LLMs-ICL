from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of player, goal, and team)
# e.g. if ingram == 1 and goals6 == 1 and checkers == 1, then Ingram scored 6 goals and is from the Checkers
ingram, parrish, quinn, underwood = players = intvar(1, 4, shape=4)
goals6, goals7, goals8, goals9 = goals = intvar(1, 4, shape=4)
checkers, comets, ice_hogs, monsters = teams = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
player_to_int = None  # N/A
goal_to_int = {goals6: 6, goals7: 7, goals8: 8, goals9: 9}  # in goals
team_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def scored_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 scored exactly diff goals more than var2.
    """
    return [((g1 == var1) & (g2 == var2)).implies(goal_to_int[g1] == goal_to_int[g2] + diff)
            for g1 in goals for g2 in goals]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(players)
m += AllDifferent(goals)
m += AllDifferent(teams)

# Clue 1: Ingram had 7 goals this season:
m += ingram == goals7

# Clue 2: The four players are Underwood, the player from the Ice Hogs, the player from the Monsters and the player from the Checkers:
m += AllDifferent([underwood, ice_hogs, monsters, checkers])

# Clue 3: Parrish scored 1 goal more than Quinn:
m += scored_exactly_more_than(parrish, quinn, 1)

# Clue 4: The player with 9 goals is from the Ice Hogs:
m += goals9 == ice_hogs

# Clue 5: Ingram is either the player from the Checkers or the player with 6 goals:
m += Xor([
    ingram == checkers,
    ingram == goals6
])

