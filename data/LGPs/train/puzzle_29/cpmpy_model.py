from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, length, and emperor)
# e.g. if belinda == 1 and minutes6 == 1 and augustus == 1, then Belinda spoke for 6 minutes about Augustus
belinda, ivan, neal, zachary = names = intvar(1, 4, shape=4)
minutes6, minutes8, minutes10, minutes12 = lengths = intvar(1, 4, shape=4)
augustus, constantine, hadrian, licinius = emperors = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
length_to_int = {minutes6: 6, minutes8: 8, minutes10: 10, minutes12: 12}  # in minutes
emperor_to_int = None  # N/A


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
m += AllDifferent(emperors)

# Clue 1: The presenter who gave the presentation on Hadrian spoke 4 minutes more than Ivan:
m += spoke_exactly_more_than(hadrian, ivan, 4)

# Clue 2: Neal spoke 4 minutes more than the student who gave the presentation on Licinius:
m += spoke_exactly_more_than(neal, licinius, 4)

# Clue 3: Ivan talked about Constantine:
m += ivan == constantine

# Clue 4: Ivan spoke 2 minutes less than Zachary:
m += spoke_exactly_more_than(zachary, ivan, 2)

