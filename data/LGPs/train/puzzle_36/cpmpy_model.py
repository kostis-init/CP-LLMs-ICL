from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of rocket, month, and company)
# e.g. if beritron == 1 and january == 1 and omnipax == 1, then Beritron will launch in January and developed by Omnipax
beritron, exatris, foltron, worul = rockets = intvar(1, 4, shape=4)
january, february, march, april = months = intvar(1, 4, shape=4)
omnipax, rubicorp, spacezen, ubersplore = companies = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
rocket_to_int = None  # N/A
month_to_int = {january: 1, february: 2, march: 3, april: 4}  # in months
company_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def launched_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 launched exactly diff months after var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] == month_to_int[m2] + diff)
            for m1 in months for m2 in months]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(rockets)
m += AllDifferent(months)
m += AllDifferent(companies)

# Clue 1: The Exatris will launch 1 month after the Worul:
m += launched_exactly_after_than(exatris, worul, 1)

# Clue 2: Of the Foltron and the rocket that will launch in January, one is made by Ubersplore and the other is made by Rubicorp:
m += Xor([
    (foltron == ubersplore) & (january == rubicorp),
    (foltron == rubicorp) & (january == ubersplore)
])

# Clue 3: The rocket developed by SpaceZen will launch 2 months after the rocket developed by Ubersplore:
m += launched_exactly_after_than(spacezen, ubersplore, 2)

# Clue 4: The rocket that will launch in February is either the Worul or the rocket developed by Omnipax:
m += Xor([
    february == worul,
    february == omnipax
])

