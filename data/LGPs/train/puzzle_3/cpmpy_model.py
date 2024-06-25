from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, month, and company)
# e.g. if cornick == 1 and january == 1 and permias == 1, then Cornick will launch in January and developed by Permias
cornick, dreadco, foltron, worul = names = intvar(1, 4, shape=4)
january, february, march, april = months = intvar(1, 4, shape=4)
permias, rubicorp, techtrin, ubersplore = companies = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
month_to_int = {january: 1, february: 2, march: 3, april: 4}  # in months
company_to_int = None  # N/A


def launched_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 launched exactly diff months after var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] == month_to_int[m2] + diff)
            for m1 in months for m2 in months]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(months)
m += AllDifferent(companies)

# Clue 1: The Worul, the rocket that will launch in February and the rocket that will launch in January are all different rockets:
m += AllDifferent([worul, february, january])

# Clue 2: The Dreadco is made by Ubersplore:
m += dreadco == ubersplore

# Clue 3: The rocket developed by Permias will launch 1 month before the Foltron:
m += launched_exactly_after_than(permias, foltron, -1)

# Clue 4: The rocket that will launch in January is made by Techtrin:
m += january == techtrin
