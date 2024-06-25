from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of waterfall, height, and country)
# e.g. if sihat == 1 and height100 == 1 and brazil == 1, then Sihat is 100 ft tall and located in Brazil
sihat, rhoqua, nyalt, inawatai = waterfalls = intvar(1, 4, shape=4)
height100, height105, height110, height115 = heights = intvar(1, 4, shape=4)
brazil, nigeria, tibet, switzerland = countries = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
waterfall_to_int = None  # N/A
height_to_int = {height100: 100, height105: 105, height110: 110, height115: 115}  # in feet
country_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def taller_than(var1, var2):
    """
    Formulate the constraint that var1 is taller than var2.
    """
    return [((h1 == var1) & (h2 == var2)).implies(height_to_int[h1] > height_to_int[h2])
            for h1 in heights for h2 in heights]


def exactly_taller_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is exactly diff ft taller than var2.
    """
    return [((h1 == var1) & (h2 == var2)).implies(height_to_int[h1] == height_to_int[h2] + diff)
            for h1 in heights for h2 in heights]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(waterfalls)
m += AllDifferent(heights)
m += AllDifferent(countries)

# Clue 1: The 115 ft tall waterfall is either the waterfall in Nigeria or the waterfall located in Tibet:
m += Xor([
    height115 == nigeria,
    height115 == tibet
])

# Clue 2: Inawatai is 100 ft tall:
m += inawatai == height100

# Clue 3: Nyalt is 10 ft taller than Rhoqua:
m += exactly_taller_than(nyalt, rhoqua, 10)

# Clue 4: The waterfall in Brazil is somewhat shorter than Rhoqua:
m += taller_than(rhoqua, brazil)

# Clue 5: The waterfall in Brazil is 10 ft shorter than the waterfall located in Nigeria:
m += exactly_taller_than(nigeria, brazil, 10)

