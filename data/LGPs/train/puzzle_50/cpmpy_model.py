from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of player, games, and position)
# e.g. if charles == 1 and games8 == 1 and center_field == 1, then Charles played 8 games in center field
charles, evan, karl, vincent = players = intvar(1, 4, shape=4)
games8, games9, games10, games11 = games = intvar(1, 4, shape=4)
center_field, first_base, shortstop, third_base = positions = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
player_to_int = None  # N/A
games_to_int = {games8: 8, games9: 9, games10: 10, games11: 11}  # in games
position_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def played_exactly_more_games_than(var1, var2, diff):
    """
    Formulate the constraint that var1 played diff more games than var2.
    """
    return [((g1 == var1) & (g2 == var2)).implies(games_to_int[g1] == games_to_int[g2] + diff)
            for g1 in games for g2 in games]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(players)
m += AllDifferent(games)
m += AllDifferent(positions)

# Clue 1: Evan played 9 games:
m += evan == games9

# Clue 2: Vincent played first base:
m += vincent == first_base

# Clue 3: The player who played third base played 2 more games than the person who played center field:
m += played_exactly_more_games_than(third_base, center_field, 2)

# Clue 4: Charles played 2 more games than the player who played center field:
m += played_exactly_more_games_than(charles, center_field, 2)

# Clue 5: Charles was either the boy who played 9 games or the person who played 10 games:
m += Xor([
    charles == games9,
    charles == games10
])

