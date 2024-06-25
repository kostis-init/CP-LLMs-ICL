from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of island, year, and culture)
# e.g. if fushil == 1 and year1754 == 1 and hakili == 1, then Fushil was discovered in 1754 and is the island of the Hakili people
fushil, jujihm, nuhirk, verinya = islands = intvar(1, 4, shape=4)
year1754, year1761, year1768, year1775 = years = intvar(1, 4, shape=4)
hakili, manikai, kukani, wainani = cultures = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
island_to_int = None  # N/A
year_to_int = {year1754: 1754, year1761: 1761, year1768: 1768, year1775: 1775}  # in years
culture_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def discovered_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 was discovered exactly diff years after var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] == year_to_int[y2] + diff)
            for y1 in years for y2 in years]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(islands)
m += AllDifferent(years)
m += AllDifferent(cultures)

# Clue 1: Jujihm was discovered in 1768:
m += jujihm == year1768

# Clue 2: Verinya was discovered in 1761:
m += verinya == year1761

# Clue 3: Jujihm was discovered 14 years after the island on which the Wainani people lived:
m += discovered_exactly_after_than(jujihm, wainani, 14)

# Clue 4: The island on which the Kukani people lived was discovered 7 years after Fushil:
m += discovered_exactly_after_than(kukani, fushil, 7)

# Clue 5: The island discovered in 1768 was either the island on which the Hakili people lived or Fushil:
m += Xor([
    year1768 == hakili,
    year1768 == fushil
])

