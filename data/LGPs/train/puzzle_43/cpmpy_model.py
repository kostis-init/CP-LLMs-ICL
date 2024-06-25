from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of presenter, day, and topic)
# e.g. if alexander == 1 and may10 == 1 and global_warming == 1, then Alexander is presenting on global warming on May 10th
alexander, gerard, inez, mable = presenters = intvar(1, 4, shape=4)
may10, may11, may12, may13 = days = intvar(1, 4, shape=4)
global_warming, nitrogen_usage, sulfur_oxide, wind_power = topics = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
presenter_to_int = None  # N/A
day_to_int = {may10: 10, may11: 11, may12: 12, may13: 13}  # in May days
topic_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def scheduled_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is scheduled exactly diff days after var2.
    """
    return [((d1 == var1) & (d2 == var2)).implies(day_to_int[d1] == day_to_int[d2] + diff)
            for d1 in days for d2 in days]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(presenters)
m += AllDifferent(days)
m += AllDifferent(topics)

# Clue 1: The sulfur oxide expert is scheduled 1 day after Gerard:
m += scheduled_exactly_after_than(sulfur_oxide, gerard, 1)

# Clue 2: The nitrogen usage expert is scheduled 1 day before Alexander:
m += scheduled_exactly_after_than(alexander, nitrogen_usage, 1)

# Clue 3: Inez will discuss global warming:
m += inez == global_warming

# Clue 4: Mable is scheduled 2 days after the sulfur oxide expert:
m += scheduled_exactly_after_than(mable, sulfur_oxide, 2)
