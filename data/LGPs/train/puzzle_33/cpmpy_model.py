from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of flier, month, and lucky charm)
# e.g. if katie == 1 and january == 1 and coin == 1, then Katie will leave in January with the coin
katie, neal, troy, yolanda = fliers = intvar(1, 4, shape=4)
january, february, march, april = months = intvar(1, 4, shape=4)
coin, rabbits_foot, talisman, wishbone = lucky_charms = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
flier_to_int = None  # N/A
month_to_int = {january: 1, february: 2, march: 3, april: 4}  # in months
lucky_charm_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def leaves_exactly_before_than(var1, var2, diff):
    """
    Formulate the constraint that var1 leaves diff months before var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] == month_to_int[m2] - diff)
            for m1 in months for m2 in months]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(fliers)
m += AllDifferent(months)
m += AllDifferent(lucky_charms)

# Clue 1: The passenger with the wishbone is either Troy or Neal:
m += Xor([
    wishbone == troy,
    wishbone == neal
])

# Clue 2: The four fliers are the passenger with the rabbit's foot, the passenger leaving in April, Yolanda and the passenger leaving in February:
m += AllDifferent([rabbits_foot, april, yolanda, february])

# Clue 3: The aerophobe leaving in March is either the aerophobe with the wishbone or the passenger with the talisman:
m += Xor([
    march == wishbone,
    march == talisman
])

# Clue 4: The passenger with the rabbit's foot will leave 1 month before the passenger with the coin:
m += leaves_exactly_before_than(rabbits_foot, coin, 1)

# Clue 5: Neal will leave in February:
m += neal == february
