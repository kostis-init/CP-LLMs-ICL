from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, packsize, and brand)
# e.g. if arthur == 1 and liter25 == 1 and adironda == 1, then Arthur's pack is a 25 liter pack made by Adironda
arthur, eugene, natasha, olga = names = intvar(1, 4, shape=4)
liter25, liter30, liter35, liter40 = packsize = intvar(1, 4, shape=4)
adironda, grennel, naturba, travelore = brands = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
packsize_to_int = {liter25: 25, liter30: 30, liter35: 35, liter40: 40}  # in liters
brand_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def pack_exactly_larger_than(var1, var2, diff):
    """
    Formulate the constraint that var1's pack is diff liters larger than var2's pack.
    """
    return [((p1 == var1) & (p2 == var2)).implies(packsize_to_int[p1] == packsize_to_int[p2] + diff)
            for p1 in packsize for p2 in packsize]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(packsize)
m += AllDifferent(brands)

# Clue 1: Arthur's pack is either the 25 liter pack or the Adironda pack:
m += Xor([
    arthur == liter25,
    arthur == adironda
])

# Clue 2: Eugene's pack is made by Adironda:
m += eugene == adironda

# Clue 3: Natasha's pack is either the 40 liter pack or the Travelore pack:
m += Xor([
    natasha == liter40,
    natasha == travelore
])

# Clue 4: Natasha's pack is 10 liters larger than the Grennel pack:
m += pack_exactly_larger_than(natasha, grennel, 10)

# Clue 5: The 30 liter pack is made by Grennel:
m += liter30 == grennel

