from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of arena, capacity, and sport)
# e.g. if gentry == 1 and capacity110 == 1 and basketball == 1, then Gentry has a capacity of 110 and is for basketball
gentry, underwood, vazquez, young = arenas = intvar(1, 4, shape=4)
capacity110, capacity150, capacity190, capacity230 = capacities = intvar(1, 4, shape=4)
basketball, football, lacrosse, soccer = sports = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
arena_to_int = None  # N/A
capacity_to_int = {capacity110: 110, capacity150: 150, capacity190: 190, capacity230: 230}  # in people
sport_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def holds_more_than(var1, var2):
    """
    Formulate the constraint that var1 holds more people than var2.
    """
    return [((c1 == var1) & (c2 == var2)).implies(capacity_to_int[c1] > capacity_to_int[c2])
            for c1 in capacities for c2 in capacities]


def holds_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 holds exactly diff more people than var2.
    """
    return [((c1 == var1) & (c2 == var2)).implies(capacity_to_int[c1] == capacity_to_int[c2] + diff)
            for c1 in capacities for c2 in capacities]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(arenas)
m += AllDifferent(capacities)
m += AllDifferent(sports)

# Clue 1: The football facility holds more people than Underwood Arena:
m += holds_more_than(football, underwood)

# Clue 2: The basketball facility holds 80 more people than Vazquez Arena:
m += holds_exactly_more_than(basketball, vazquez, 80)

# Clue 3: Young Arena holds 230 people:
m += young == capacity230

# Clue 4: Underwood Arena holds 40 fewer people than Vazquez Arena:
m += holds_exactly_more_than(vazquez, underwood, 40)

# Clue 5: The facility with seating for 190 people is either the lacrosse facility or Underwood Arena:
m += Xor([
    capacity190 == lacrosse,
    capacity190 == underwood
])

