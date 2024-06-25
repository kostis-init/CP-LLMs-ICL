from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, length, and prime minister)
# e.g. if anita == 1 and minutes6 == 1 and chamberlain == 1, then Anita spoke for 6 minutes about Chamberlain
anita, colleen, perry, theodore = names = intvar(1, 4, shape=4)
minutes6, minutes8, minutes10, minutes12 = lengths = intvar(1, 4, shape=4)
chamberlain, churchill, gladstone, heath = prime_ministers = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
length_to_int = {minutes6: 6, minutes8: 8, minutes10: 10, minutes12: 12}  # in minutes
prime_minister_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def spoke_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 spoke diff minutes more than var2.
    """
    return [((l1 == var1) & (l2 == var2)).implies(length_to_int[l1] == length_to_int[l2] + diff)
            for l1 in lengths for l2 in lengths]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(lengths)
m += AllDifferent(prime_ministers)

# Clue 1: The student who spoke for 12 minutes talked about Churchill:
m += (minutes12 == churchill)

# Clue 2: Anita was either the presenter who spoke for 10 minutes or the presenter who gave the presentation on Gladstone:
m += Xor([
    anita == minutes10,
    anita == gladstone
])

# Clue 3: Perry spoke 4 minutes more than the presenter who gave the presentation on Gladstone:
m += spoke_exactly_more_than(perry, gladstone, 4)

# Clue 4: Colleen was either the presenter who spoke for 10 minutes or the student who gave the presentation on Gladstone:
m += Xor([
    colleen == minutes10,
    colleen == gladstone
])

# Clue 5: The presenter who gave the presentation on Chamberlain spoke 2 minutes less than Colleen:
m += spoke_exactly_more_than(colleen, chamberlain, 2)
