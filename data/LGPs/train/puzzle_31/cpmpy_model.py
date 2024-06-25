from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, points, and order)
# e.g. if clara == 1 and points181 == 1 and second == 1, then Clara scored 181 points and danced second
clara, fannie, hannah, kara = names = intvar(1, 4, shape=4)
points181, points184, points187, points190 = points = intvar(1, 4, shape=4)
second, fourth, sixth, seventh = orders = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
points_to_int = {points181: 181, points184: 184, points187: 187, points190: 190}  # in points
order_to_int = {second: 2, fourth: 4, sixth: 6, seventh: 7}  # in order


# Helper functions (for formulating comparison constraints)
def scored_higher_than(var1, var2):
    """
    Formulate the constraint that var1 scored higher than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(points_to_int[p1] > points_to_int[p2])
            for p1 in points for p2 in points]


def scored_exactly_higher_than(var1, var2, diff):
    """
    Formulate the constraint that var1 scored exactly diff points higher than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(points_to_int[p1] == points_to_int[p2] + diff)
            for p1 in points for p2 in points]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(points)
m += AllDifferent(orders)

# Clue 1: The person who danced seventh scored somewhat higher than the dancer who performed fourth:
m += scored_higher_than(seventh, fourth)

# Clue 2: The dancer who performed second scored 3 points lower than the dancer who performed fourth:
m += scored_exactly_higher_than(fourth, second, 3)

# Clue 3: Kara scored somewhat lower than Fannie:
m += scored_higher_than(fannie, kara)

# Clue 4: Hannah was either the dancer who performed fourth or the person who danced sixth:
m += Xor([
    hannah == fourth,
    hannah == sixth
])

# Clue 5: Of Clara and Kara, one scored 184 points and the other danced seventh:
m += Xor([
    (clara == points184) & (kara == seventh),
    (clara == seventh) & (kara == points184)
])
