from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of employee, riders served, and section)
# e.g. if herbert == 1 and riders50 == 1 and green == 1, then Herbert served 50 riders and works in the green section
herbert, marc, nathan, victor = employees = intvar(1, 4, shape=4)
riders50, riders75, riders100, riders125 = riders_served = intvar(1, 4, shape=4)
green, pink, purple, red = sections = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
employee_to_int = None  # N/A
riders_to_int = {riders50: 50, riders75: 75, riders100: 100, riders125: 125}  # in riders
section_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def served_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 served diff more riders than var2.
    """
    return [((r1 == var1) & (r2 == var2)).implies(riders_to_int[r1] == riders_to_int[r2] + diff)
            for r1 in riders_served for r2 in riders_served]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(employees)
m += AllDifferent(riders_served)
m += AllDifferent(sections)

# Clue 1: Herbert served 25 fewer riders than Marc:
m += served_exactly_more_than(marc, herbert, 25)

# Clue 2: The worker who served 125 riders works in the red section:
m += riders125 == red

# Clue 3: Of the person who works in the pink section and the person who served 100 riders, one is Herbert and the other is Marc:
m += Xor([
    (pink == herbert) & (riders100 == marc),
    (pink == marc) & (riders100 == herbert)
])

# Clue 4: Victor is either the employee who served 50 riders or the employee who works in the purple section:
m += Xor([
    victor == riders50,
    victor == purple
])
