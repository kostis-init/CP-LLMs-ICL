from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of age, date, and profession)
# e.g. if dean == 1 and age22 == 1 and accountant == 1, then Dean is 22 years old and is an accountant
dean, jesus, max, vincent = dates = intvar(1, 4, shape=4)
age22, age23, age24, age25 = ages = intvar(1, 4, shape=4)
accountant, boxer, firefighter, musician = professions = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
date_to_int = None  # N/A
age_to_int = {age22: 22, age23: 23, age24: 24, age25: 25}  # in years
profession_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)

def is_exactly_older_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is diff years older than var2.
    """
    return [((a1 == var1) & (a2 == var2)).implies(age_to_int[a1] == age_to_int[a2] + diff)
            for a1 in ages for a2 in ages]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(dates)
m += AllDifferent(ages)
m += AllDifferent(professions)

# Clue 1: The 25 years old was the musician:
m += age25 == musician

# Clue 2: Of the musician and the accountant, one was 22 years old and the other was Max:
m += Xor([
    (musician == age22) & (accountant == max),
    (musician == max) & (accountant == age22)
])

# Clue 3: Dean was 1 year younger than Jesus:
m += is_exactly_older_than(jesus, dean, 1)

# Clue 4: The 24 years old was the firefighter:
m += age24 == firefighter

# Clue 5: The boxer was 1 year older than Dean:
m += is_exactly_older_than(boxer, dean, 1)
