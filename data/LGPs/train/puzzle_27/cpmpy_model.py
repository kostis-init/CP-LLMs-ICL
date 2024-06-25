from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of year, name, and scientist)
# e.g. if bale_hahn == 1 and year2016 == 1 and dr_farley == 1, then Bale-Hahn SSC will go online in 2016 and is headed by Dr. Farley
bale_hahn, egert, ison_x42, zynga = names = intvar(1, 4, shape=4)
year2016, year2017, year2018, year2019 = years = intvar(1, 4, shape=4)
dr_farley, dr_golden, dr_owens, dr_weber = scientists = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
year_to_int = {year2016: 2016, year2017: 2017, year2018: 2018, year2019: 2019}  # in years
scientist_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def goes_online_after(var1, var2):
    """
    Formulate the constraint that var1 goes online after var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] > year_to_int[y2])
            for y1 in years for y2 in years]


def goes_online_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 goes online exactly diff years after var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] == year_to_int[y2] + diff)
            for y1 in years for y2 in years]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(years)
m += AllDifferent(scientists)

# Clue 1: The project headed by Dr. Golden will go online sometime before the Zynga Complex:
m += goes_online_after(zynga, dr_golden)

# Clue 2: The project headed by Dr. Weber will go online 1 year before the Bale-Hahn SSC:
m += goes_online_exactly_after_than(bale_hahn, dr_weber, 1)

# Clue 3: The Egert Facility will go online 1 year after the ISON-X42:
m += goes_online_exactly_after_than(egert, ison_x42, 1)

# Clue 4: The project headed by Dr. Owens will go online 1 year after the ISON-X42:
m += goes_online_exactly_after_than(dr_owens, ison_x42, 1)

