from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of runner, time, and color)
# e.g. if franklin == 1 and time21 == 1 and aquamarine == 1, then Franklin wore the aquamarine shirt and finished in 21 minutes
franklin, salvador, ted, zachary = runners = intvar(1, 4, shape=4)
time21, time22, time23, time24 = times = intvar(1, 4, shape=4)
aquamarine, black, cyan, maroon = colors = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
runner_to_int = None  # N/A
time_to_int = {time21: 21, time22: 22, time23: 23, time24: 24}  # in minutes
color_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def finished_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 finished exactly diff minutes after var2.
    """
    return [((t1 == var1) & (t2 == var2)).implies(time_to_int[t1] == time_to_int[t2] + diff)
            for t1 in times for t2 in times]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(runners)
m += AllDifferent(times)
m += AllDifferent(colors)

# Clue 1: Zachary wore the aquamarine shirt:
m += zachary == aquamarine

# Clue 2: The contestant in the cyan shirt finished 1 minute after Franklin:
m += finished_exactly_after_than(cyan, franklin, 1)

# Clue 3: Zachary finished 2 minutes after Salvador:
m += finished_exactly_after_than(zachary, salvador, 2)

# Clue 4: The contestant in the maroon shirt finished 1 minute before Salvador:
m += finished_exactly_after_than(maroon, salvador, -1)

