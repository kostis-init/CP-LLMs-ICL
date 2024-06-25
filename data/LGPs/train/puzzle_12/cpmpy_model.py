from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of miner, ounces, and claim)
# e.g. if fred == 1 and ounces11 == 1 and belle_hart == 1, then Fred Fletcher found 11 ounces at Belle Hart
fred, gil, ivan, jack = miners = intvar(1, 4, shape=4)
ounces11, ounces14, ounces17, ounces20 = ounces = intvar(1, 4, shape=4)
belle_hart, culver_gorge, fuller_rise, york_river = claims = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
miner_to_int = None  # N/A
ounces_to_int = {ounces11: 11, ounces14: 14, ounces17: 17, ounces20: 20}  # in ounces
claim_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def found_more_gold_than(var1, var2):
    """
    Formulate the constraint that var1 found more gold than var2.
    """
    return [((o1 == var1) & (o2 == var2)).implies(ounces_to_int[o1] > ounces_to_int[o2])
            for o1 in ounces for o2 in ounces]


def found_exactly_more_gold_than(var1, var2, diff):
    """
    Formulate the constraint that var1 found exactly diff ounces more gold than var2.
    """
    return [((o1 == var1) & (o2 == var2)).implies(ounces_to_int[o1] == ounces_to_int[o2] + diff)
            for o1 in ounces for o2 in ounces]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(miners)
m += AllDifferent(ounces)
m += AllDifferent(claims)

# Clue 1: The prospector who found 11 ounces of gold was either the prospector working at Fuller Rise or the prospector working at Culver Gorge:
m += Xor([
    ounces11 == fuller_rise,
    ounces11 == culver_gorge
])

# Clue 2: The prospector who found 20 ounces of gold worked at the Fuller Rise claim:
m += ounces20 == fuller_rise

# Clue 3: Ivan Ingram found 14 ounces of gold:
m += ivan == ounces14

# Clue 4: The miner working at Belle Hart finished with 6 ounces more gold than Fred Fletcher:
m += found_exactly_more_gold_than(belle_hart, fred, 6)

# Clue 5: Jack Jacobs finished with somewhat less gold than Gil Gonzalez:
m += found_more_gold_than(gil, jack)

