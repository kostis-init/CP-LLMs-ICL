from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, year, and suit color)
# e.g. if jorge == 1 and year1982 == 1 and red == 1, then Jorge wears a red suit and started in 1982
jorge, otis, philip, shaun = names = intvar(1, 4, shape=4)
year1982, year1983, year1984, year1985 = years = intvar(1, 4, shape=4)
lime_green, pink, red, yellow = suit_colors = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
year_to_int = {year1982: 1982, year1983: 1983, year1984: 1984, year1985: 1985}  # in years
suit_color_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def started_after_than(var1, var2):
    """
    Formulate the constraint that var1 started skydiving after var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] > year_to_int[y2])
            for y1 in years for y2 in years]


def started_exactly_before_than(var1, var2, diff):
    """
    Formulate the constraint that var1 started skydiving exactly diff years before var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y2] == year_to_int[y1] + diff)
            for y1 in years for y2 in years]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(years)
m += AllDifferent(suit_colors)

# Clue 1: Jorge is either the skydiver who wears the red suit or the jumper who started in 1982:
m += Xor([
    jorge == red,
    jorge == year1982
])

# Clue 2: The skydiver who wears the pink suit started skydiving 1 year before Otis:
m += started_exactly_before_than(pink, otis, 1)

# Clue 3: The jumper who wears the yellow suit started skydiving sometime after Philip:
m += started_after_than(yellow, philip)

# Clue 4: The jumper who wears the lime green suit started skydiving sometime after the jumper who wears the yellow suit:
m += started_after_than(lime_green, yellow)

# Clue 5: The jumper who wears the pink suit started skydiving 2 years before Shaun:
m += started_exactly_before_than(pink, shaun, 2)

