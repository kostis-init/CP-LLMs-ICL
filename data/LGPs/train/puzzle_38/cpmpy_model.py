from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of age, tortoise, and species)
# e.g. if chewie == 1 and age14 == 1 and black_neck == 1, then Chewie is 14 years old and is a black neck tortoise
chewie, snappy, speedy, toredo = tortoises = intvar(1, 4, shape=4)
age14, age32, age50, age68 = ages = intvar(1, 4, shape=4)
black_neck, horned, pitch_belly, swoopbacked = species = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
tortoise_to_int = None  # N/A
age_to_int = {age14: 14, age32: 32, age50: 50, age68: 68}  # in years
species_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def older_than(var1, var2):
    """
    Formulate the constraint that var1 is older than var2.
    """
    return [((a1 == var1) & (a2 == var2)).implies(age_to_int[a1] > age_to_int[a2])
            for a1 in ages for a2 in ages]


def exactly_younger_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is exactly diff years younger than var2.
    """
    return [((a1 == var1) & (a2 == var2)).implies(age_to_int[a1] == age_to_int[a2] - diff)
            for a1 in ages for a2 in ages]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(tortoises)
m += AllDifferent(ages)
m += AllDifferent(species)

# Clue 1: Snappy is 18 years younger than the swoopbacked tortoise:
m += exactly_younger_than(snappy, swoopbacked, 18)

# Clue 2: The 68 year old animal is the horned tortoise:
m += age68 == horned

# Clue 3: Chewie is 32 years old:
m += chewie == age32

# Clue 4: Of Snappy and Toredo, one is 14 years old and the other is the horned tortoise:
m += Xor([
    (snappy == age14) & (toredo == horned),
    (snappy == horned) & (toredo == age14)
])

# Clue 5: The pitch belly tortoise is younger than Chewie:
m += older_than(chewie, pitch_belly)

