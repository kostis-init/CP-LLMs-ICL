from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of employee, riders served, and section)
# e.g. if brett == 1 and riders50 == 1 and blue == 1, then Brett served 50 riders and works in the blue section
brett, peter, victor, willis = employees = intvar(1, 4, shape=4)
riders50, riders75, riders100, riders125 = riders_served = intvar(1, 4, shape=4)
blue, green, orange, yellow = sections = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
employee_to_int = None  # N/A
riders_to_int = {riders50: 50, riders75: 75, riders100: 100, riders125: 125}  # in number of riders
section_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def served_more_than(var1, var2):
    """
    Formulate the constraint that var1 served more riders than var2.
    """
    return [((r1 == var1) & (r2 == var2)).implies(riders_to_int[r1] > riders_to_int[r2])
            for r1 in riders_served for r2 in riders_served]


def served_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 served exactly diff riders more than var2.
    """
    return [((r1 == var1) & (r2 == var2)).implies(riders_to_int[r1] == riders_to_int[r2] + diff)
            for r1 in riders_served for r2 in riders_served]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(employees)
m += AllDifferent(riders_served)
m += AllDifferent(sections)

# Clue 1: The worker who works in the green section served more riders than Brett:
m += served_more_than(green, brett)

# Clue 2: Peter served 25 fewer riders than Willis:
m += served_exactly_more_than(willis, peter, 25)

# Clue 3: Brett served more riders than Peter:
m += served_more_than(brett, peter)

# Clue 4: The person who works in the yellow section served 25 more riders than the worker who works in the orange section:
m += served_exactly_more_than(yellow, orange, 25)

# Clue 5: Peter is either the person who served 125 riders or the person who works in the blue section:
m += Xor([
    peter == riders125,
    peter == blue
])

