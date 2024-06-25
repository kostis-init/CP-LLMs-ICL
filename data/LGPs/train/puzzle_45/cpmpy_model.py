from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of borrower, due date, and title)
# e.g. if cory == 1 and sep1 == 1 and dancing_well == 1, then Cory took out Dancing Well due on September 1
cory, rosa, sherrie, vicki = borrowers = intvar(1, 4, shape=4)
sep1, sep8, sep15, sep22 = due_dates = intvar(1, 4, shape=4)
dancing_well, heavens_seal, stars_below, time_to_burn = titles = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
borrower_to_int = None  # N/A
due_date_to_int = {sep1: 1, sep8: 8, sep15: 15, sep22: 22}  # in September dates
title_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def due_exactly_before_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is due exactly diff days before var2.
    """
    return [((d1 == var1) & (d2 == var2)).implies(due_date_to_int[d1] == due_date_to_int[d2] - diff)
            for d1 in due_dates for d2 in due_dates]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(borrowers)
m += AllDifferent(due_dates)
m += AllDifferent(titles)

# Clue 1: The four books are Rosa's book, the book due on September 22, Dancing Well and the book due on September 15:
m += AllDifferent([rosa, sep22, dancing_well, sep15])

# Clue 2: Heaven's Seal is either Vicki's book or the book due on September 8:
m += Xor([
    heavens_seal == vicki,
    heavens_seal == sep8
])

# Clue 3: Of Heaven's Seal and the title due on September 22, one was taken out by Cory and the other was taken out by Vicki:
m += Xor([
    (heavens_seal == cory) & (sep22 == vicki),
    (heavens_seal == vicki) & (sep22 == cory)
])

# Clue 4: Sherrie's book was due 2 weeks before Stars Below:
m += due_exactly_before_than(sherrie, stars_below, 14)

