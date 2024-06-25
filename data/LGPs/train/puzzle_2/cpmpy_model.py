from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of diplomat, month, and duration)
# e.g. if gilbert == 1 and january == 1 and days4 == 1, then Gilbert will leave in January and for 4 days
gilbert, macdonald, pickett, vasquez = diplomats = intvar(1, 4, shape=4)
january, february, march, april = months = intvar(1, 4, shape=4)
days4, days5, days9, days10 = durations = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
diplomat_to_int = None  # N/A
month_to_int = {january: 1, february: 2, march: 3, april: 4}  # in months
duration_to_int = {days4: 4, days5: 5, days9: 9, days10: 10}  # in days


# Helper functions (for formulating comparison constraints)
def left_after_than(var1, var2):
    """
    Formulate the constraint that var1 left after var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] > month_to_int[m2])
            for m1 in months for m2 in months]


def left_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 left exactly diff months after var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] == month_to_int[m2] + diff)
            for m1 in months for m2 in months]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(diplomats)
m += AllDifferent(months)
m += AllDifferent(durations)

# Clue 1: Vasquez will leave sometime after Macdonald:
m += left_after_than(vasquez, macdonald)

# Clue 2: Vasquez will leave 1 month before the ambassador with the 5-day visit:
m += left_exactly_after_than(vasquez, days5, -1)

# Clue 3: Gilbert is either the person leaving in January or the ambassador with the 4-day visit:
m += Xor([
    gilbert == january,
    gilbert == days4
])

# Clue 4: Macdonald will leave 1 month before the ambassador with the 4-day visit:
m += left_exactly_after_than(macdonald, days4, -1)

# Clue 5: The ambassador with the 4-day visit will leave sometime before the ambassador with the 9-day visit:
m += left_after_than(days9, days4)
