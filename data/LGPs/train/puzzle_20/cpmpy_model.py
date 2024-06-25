from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, age, and state)
# e.g. if arlene == 1 and age109 == 1 and kansas == 1, then Arlene is 109 years old and from Kansas
arlene, ernesto, kyle, willard = names = intvar(1, 4, shape=4)
age109, age110, age111, age112 = ages = intvar(1, 4, shape=4)
kansas, louisiana, pennsylvania, south_dakota = states = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
age_to_int = {age109: 109, age110: 110, age111: 111, age112: 112}  # in years
state_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def older_than(var1, var2):
    """
    Formulate the constraint that var1 is older than var2.
    """
    return [((a1 == var1) & (a2 == var2)).implies(age_to_int[a1] > age_to_int[a2])
            for a1 in ages for a2 in ages]


def exactly_older_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is exactly diff years older than var2.
    """
    return [((a1 == var1) & (a2 == var2)).implies(age_to_int[a1] == age_to_int[a2] + diff)
            for a1 in ages for a2 in ages]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(ages)
m += AllDifferent(states)

# Clue 1: Kyle is 1 year older than Arlene:
m += exactly_older_than(kyle, arlene, 1)

# Clue 2: Kyle, the centenarian who is 109 years old and the person who is 110 years old are all different people:
m += AllDifferent([kyle, age109, age110])

# Clue 3: The Pennsylvania native is older than Ernesto:
m += older_than(pennsylvania, ernesto)

# Clue 4: Ernesto is older than the Louisiana native:
m += older_than(ernesto, louisiana)

# Clue 5: The person who is 111 years old is a native of South Dakota:
m += age111 == south_dakota

