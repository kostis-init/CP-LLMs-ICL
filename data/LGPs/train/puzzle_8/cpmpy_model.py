from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of witness, date, and town)
# e.g. if benny == 1 and aug4 == 1 and crescent == 1, then Benny Baron's sighting was submitted on August 4 from Crescent City
benny, dan, edith, gil = witnesses = intvar(1, 4, shape=4)
aug4, aug5, aug6, aug7 = dates = intvar(1, 4, shape=4)
crescent, embden, islesboro, walnut = towns = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
witness_to_int = None  # N/A
date_to_int = {aug4: 4, aug5: 5, aug6: 6, aug7: 7}  # in days
town_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
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

# Clue 1: Benny Baron's sighting was submitted 2 days after Dan Delgado's report:
m += submitted_exactly_after_than(benny, dan, 2)

# Clue 2: Of the August 7 report and the August 5 sighting, one was reported by Gil Gates and the other was from Walnut Creek:
m += Xor([
    (aug7 == gil) & (aug5 == walnut),
    (aug7 == walnut) & (aug5 == gil)
])

# Clue 3: The report from Crescent City was submitted 1 day after the sighting from Islesboro:
m += submitted_exactly_after_than(crescent, islesboro, 1)

# Clue 4: The sighting from Walnut Creek was either the August 7 report or Edith Estes's sighting:
m += Xor([
    walnut == aug7,
    walnut == edith
])

