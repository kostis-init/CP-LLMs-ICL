from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of diplomat, month, and duration)
# e.g. if fitzgerald == 1 and january == 1 and days2 == 1, then Fitzgerald will leave in January for a 2 day visit
fitzgerald, howell, riggs, vasquez = diplomats = intvar(1, 4, shape=4)
january, february, march, april = months = intvar(1, 4, shape=4)
days2, days6, days8, days9 = durations = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
diplomat_to_int = None  # N/A
month_to_int = {january: 1, february: 2, march: 3, april: 4}  # in months
duration_to_int = {days2: 2, days6: 6, days8: 8, days9: 9}  # in days


# Helper functions (for formulating comparison constraints)
def leaves_after(var1, var2):
    """
    Formulate the constraint that var1 leaves after var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] > month_to_int[m2])
            for m1 in months for m2 in months]


def leaves_exactly_after(var1, var2, diff):
    """
    Formulate the constraint that var1 leaves exactly diff months before var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] == month_to_int[m2] + diff)
            for m1 in months for m2 in months]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(diplomats)
m += AllDifferent(months)
m += AllDifferent(durations)

# Clue 1: Howell will leave sometime after Fitzgerald:
m += leaves_after(howell, fitzgerald)

# Clue 2: Howell will leave sometime before the ambassador with the 6 day visit:
m += leaves_after(days6, howell)

# Clue 3: Vasquez will leave 1 month before the ambassador with the 2 day visit:
m += leaves_exactly_after(days2, vasquez, 1)

# Clue 4: The ambassador with the 8 day visit will leave 2 months before Vasquez:
m += leaves_exactly_after(vasquez, days8, 2)

