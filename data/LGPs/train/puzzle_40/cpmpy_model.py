from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of crater, diameter, and period)
# e.g. if asanish == 1 and meters100 == 1 and cambrian == 1, then Asanish crater is 100 meters wide and formed during the Cambrian period
asanish, cersay, garight, kimeta = craters = intvar(1, 4, shape=4)
meters100, meters125, meters150, meters175 = diameters = intvar(1, 4, shape=4)
cambrian, devonian, jurassic, ordovician = periods = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
crater_to_int = None  # N/A
diameter_to_int = {meters100: 100, meters125: 125, meters150: 150, meters175: 175}  # in meters
period_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def exactly_wider_than(var1, var2, diff):
    """
    Formulate the constraint that var1 is diff meters wider than var2.
    """
    return [((d1 == var1) & (d2 == var2)).implies(diameter_to_int[d1] == diameter_to_int[d2] + diff)
            for d1 in diameters for d2 in diameters]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(craters)
m += AllDifferent(diameters)
m += AllDifferent(periods)

# Clue 1: The Garight crater is 150 meters wide:
m += garight == meters150

# Clue 2: The Cersay crater was formed during the Cambrian period:
m += cersay == cambrian

# Clue 3: The Cersay crater is 50 meters wider than the Jurassic crater:
m += exactly_wider_than(cersay, jurassic, 50)

# Clue 4: The Asanish crater is 25 meters smaller than the Ordovician crater:
m += exactly_wider_than(ordovician, asanish, 25)
