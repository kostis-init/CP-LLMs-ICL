from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, wingspan, and age)
# e.g. if merlin == 1 and inches102 == 1 and age4 == 1, then Merlin has a wingspan of 102 inches and is 4 years old
merlin, pepper, spike, sunshine = names = intvar(1, 4, shape=4)
wingspan102, wingspan106, wingspan110, wingspan114 = wingspans = intvar(1, 4, shape=4)
age4, age5, age8, age9 = ages = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
wingspan_to_int = {wingspan102: 102, wingspan106: 106, wingspan110: 110, wingspan114: 114}  # in inches
age_to_int = {age4: 4, age5: 5, age8: 8, age9: 9}  # in years


# Helper functions (for formulating comparison constraints)
def wingspan_shorter_than(var1, var2, diff):
    """
    Formulate the constraint that var1 has a wingspan diff inches shorter than var2.
    """
    return [((w1 == var1) & (w2 == var2)).implies(wingspan_to_int[w1] == wingspan_to_int[w2] - diff)
            for w1 in wingspans for w2 in wingspans]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(wingspans)
m += AllDifferent(ages)

# Clue 1: Sunshine is either the condor with a wingspan of 102 inches or the 5-year-old bird:
m += Xor([
    sunshine == wingspan102,
    sunshine == age5
])

# Clue 2: The condor with a wingspan of 114 inches is 5 years old:
m += wingspan114 == age5

# Clue 3: Pepper has a wingspan of 114 inches:
m += pepper == wingspan114

# Clue 4: The four condors are the 9-year-old bird, Pepper, Merlin and the condor with a wingspan of 106 inches:
m += AllDifferent([age9, pepper, merlin, wingspan106])

# Clue 5: The 9-year-old bird has a wingspan 4 inches shorter than the 4-year-old bird:
m += wingspan_shorter_than(age9, age4, 4)
