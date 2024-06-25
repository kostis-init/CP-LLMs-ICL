from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of crater, diameter, and period)
# e.g. if cersay == 1 and meters100 == 1 and jurassic == 1, then Cersay crater is 100 meters wide and from the Jurassic period
cersay, moriwa, ormagh, vorckin = craters = intvar(1, 4, shape=4)
meters100, meters125, meters150, meters175 = diameters = intvar(1, 4, shape=4)
jurassic, ordovician, permian, triassic = periods = intvar(1, 4, shape=4)

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

# Clue 1: The Vorckin impact crater is 125 meters wide:
m += vorckin == meters125

# Clue 2: The 150 meters wide one is either the Ordovician impact crater or the Permian impact crater:
m += Xor([
    meters150 == ordovician,
    meters150 == permian
])

# Clue 3: The Ordovician impact crater is 25 meters wider than the Jurassic impact crater:
m += exactly_wider_than(ordovician, jurassic, 25)

# Clue 4: The Triassic impact crater is either the Ormagh impact crater or the 150 meters wide one:
m += Xor([
    triassic == ormagh,
    triassic == meters150
])

# Clue 5: The Cersay impact crater was formed during the Jurassic period:
m += cersay == jurassic

