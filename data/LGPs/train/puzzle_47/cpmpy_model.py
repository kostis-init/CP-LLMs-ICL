from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of height, tree, and age)
# e.g. if evans_fir == 1 and height144 == 1 and age79 == 1, then Evan's Fir is 144 feet tall and 79 years old
evans_fir, old_jarvis, nolans_pine, zekes_spruce = trees = intvar(1, 4, shape=4)
height144, height147, height150, height153 = heights = intvar(1, 4, shape=4)
age79, age80, age96, age99 = ages = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
tree_to_int = None  # N/A
height_to_int = {height144: 144, height147: 147, height150: 150, height153: 153}  # in feet
age_to_int = {age79: 79, age80: 80, age96: 96, age99: 99}  # in years


# Helper functions (for formulating comparison constraints)
def taller_than(var1, var2):
    """
    Formulate the constraint that var1 is taller than var2.
    """
    return [((h1 == var1) & (h2 == var2)).implies(height_to_int[h1] > height_to_int[h2])
            for h1 in heights for h2 in heights]


def exactly_taller_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is diff feet taller than var2.
    """
    return [((h1 == var1) & (h2 == var2)).implies(height_to_int[h1] == height_to_int[h2] + diff)
            for h1 in heights for h2 in heights]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(trees)
m += AllDifferent(heights)
m += AllDifferent(ages)

# Clue 1: Of the 147 feet tree and the 80 years old tree, one is Nolan's Pine and the other is Zeke's Spruce:
m += Xor([
    (height147 == nolans_pine) & (age80 == zekes_spruce),
    (height147 == zekes_spruce) & (age80 == nolans_pine)
])

# Clue 2: The 96 years old tree is taller than Zeke's Spruce:
m += taller_than(age96, zekes_spruce)

# Clue 3: Of Evan's Fir and the 153 feet tree, one is 79 years old and the other is 99 years old:
m += Xor([
    (evans_fir == age79) & (height153 == age99),
    (evans_fir == age99) & (height153 == age79)
])

# Clue 4: The 96 years old tree is 3 feet shorter than the 79 years old tree:
m += exactly_taller_than(age79, age96, 3)
