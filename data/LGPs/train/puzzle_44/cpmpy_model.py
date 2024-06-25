from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of student, month, and ship)
# e.g. if eunice == 1 and march == 1 and escape == 1, then Eunice's project on the Escape starts in March
eunice, felix, natasha, stacy = students = intvar(1, 4, shape=4)
march, april, may, june = months = intvar(1, 4, shape=4)
escape, liberty, odyssey, osprey = ships = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
student_to_int = None  # N/A
month_to_int = {march: 3, april: 4, may: 5, june: 6}  # in months
ship_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def starts_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 starts exactly diff months after var2.
    """
    return [((m1 == var1) & (m2 == var2)).implies(month_to_int[m1] == month_to_int[m2] + diff)
            for m1 in months for m2 in months]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(students)
m += AllDifferent(months)
m += AllDifferent(ships)

# Clue 1: Natasha's study starts 2 months after the project on the Odyssey:
m += starts_exactly_after_than(natasha, odyssey, 2)

# Clue 2: Of the assignment on the Liberty and the assignment on the Escape, one is Felix's assignment and the other starts in March:
m += Xor([
    (liberty == felix) & (escape == march),
    (liberty == march) & (escape == felix)
])

# Clue 3: The study on the Liberty starts 2 months after Eunice's project:
m += starts_exactly_after_than(liberty, eunice, 2)
