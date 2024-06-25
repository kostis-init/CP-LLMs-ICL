from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of witness, date, and town)
# e.g. if benny == 1 and aug4 == 1 and islesboro == 1, then Benny Baron's report was received on August 4 from Islesboro
benny, edith, hal, iva = witnesses = intvar(1, 4, shape=4)
aug4, aug5, aug6, aug7 = dates = intvar(1, 4, shape=4)
islesboro, long_barn, tarzana, zearing = towns = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
witness_to_int = None  # N/A
date_to_int = {aug4: 4, aug5: 5, aug6: 6, aug7: 7}  # in days
town_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def submitted_after_than(var1, var2):
    """
    Formulate the constraint that var1 submitted after var2.
    """
    return [((w1 == var1) & (w2 == var2)).implies(date_to_int[w1] > date_to_int[w2])
            for w1 in dates for w2 in dates]


def submitted_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 submitted exactly diff days after var2.
    """
    return [((w1 == var1) & (w2 == var2)).implies(date_to_int[w1] == date_to_int[w2] + diff)
            for w1 in dates for w2 in dates]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(witnesses)
m += AllDifferent(dates)
m += AllDifferent(towns)

# Clue 1: The report from Zearing was either the August 4 report or Edith Estes's report:
m += Xor([
    zearing == aug4,
    zearing == edith
])

# Clue 2: Hal Harrison's report was submitted sometime after Iva Ingram's sighting:
m += submitted_after_than(hal, iva)

# Clue 3: The August 5 sighting was from Islesboro:
m += aug5 == islesboro

# Clue 4: The report from Tarzana was submitted 1 day before the sighting from Islesboro:
m += submitted_exactly_after_than(tarzana, islesboro, -1)

# Clue 5: Benny Baron's report was received on August 7:
m += benny == aug7
