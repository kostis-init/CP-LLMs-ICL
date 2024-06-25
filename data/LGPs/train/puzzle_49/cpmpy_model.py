from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of employee, riders, and section)
# e.g. if andy == 1 and riders50 == 1 and blue == 1, then Andy served 50 riders and works in the blue section
andy, brett, victor, zachary = employees = intvar(1, 4, shape=4)
riders50, riders75, riders100, riders125 = riders = intvar(1, 4, shape=4)
blue, green, red, yellow = sections = intvar(1, 4, shape=4)

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
            for r1 in riders for r2 in riders]


def served_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 served exactly diff more riders than var2.
    """
    return [((r1 == var1) & (r2 == var2)).implies(riders_to_int[r1] == riders_to_int[r2] + diff)
            for r1 in riders for r2 in riders]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(employees)
m += AllDifferent(riders)
m += AllDifferent(sections)

# Clue 1: The worker who works in the green section served 25 more riders than Andy:
m += served_exactly_more_than(green, andy, 25)

# Clue 2: Of the employee who works in the red section and the worker who works in the yellow section, one served 50 riders and the other is Victor:
m += Xor([
    (red == riders50) & (yellow == victor),
    (red == victor) & (yellow == riders50)
])

# Clue 3: The employee who works in the green section is either Zachary or the worker who served 100 riders:
m += Xor([
    green == zachary,
    green == riders100
])

# Clue 4: The person who works in the yellow section served 50 more riders than Zachary:
m += served_exactly_more_than(yellow, zachary, 50)

# Clue 5: Victor served more riders than the worker who works in the blue section:
m += served_more_than(victor, blue)

