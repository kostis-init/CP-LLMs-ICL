from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of superhero, year, and real name)
# e.g. if deep_shadow == 1 and year2007 == 1 and arnold == 1, then Deep Shadow started in 2007 and is Arnold Ashley
deep_shadow, green_avenger, max_fusion, ultra_hex = superheroes = intvar(1, 4, shape=4)
year2007, year2008, year2009, year2010 = years = intvar(1, 4, shape=4)
arnold, lyle, orel, red = real_names = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
superhero_to_int = None  # N/A
year_to_int = {year2007: 2007, year2008: 2008, year2009: 2009, year2010: 2010}  # in years
real_name_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def started_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 started exactly diff years after var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] == year_to_int[y2] + diff)
            for y1 in years for y2 in years]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(superheroes)
m += AllDifferent(years)
m += AllDifferent(real_names)

# Clue 1: The four people are the person who started in 2007, Green Avenger, Deep Shadow and Lyle Lucas:
m += AllDifferent([year2007, green_avenger, deep_shadow, lyle])

# Clue 2: Arnold Ashley began 1 year after Ultra Hex:
m += started_exactly_after_than(arnold, ultra_hex, 1)

# Clue 3: The person who started in 2009 is Arnold Ashley:
m += year2009 == arnold

# Clue 4: Green Avenger is Orel Osborne:
m += green_avenger == orel

