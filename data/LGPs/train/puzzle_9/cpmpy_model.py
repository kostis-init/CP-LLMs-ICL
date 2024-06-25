from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of car, distance, and speed)
# e.g. if awick == 1 and miles525 == 1 and speed62 == 1, then Awick drove 525 miles at a high speed of 62 MPH
awick, leden, poltris, versem = cars = intvar(1, 4, shape=4)
miles525, miles550, miles575, miles600 = distances = intvar(1, 4, shape=4)
speed62, speed69, speed75, speed81 = speeds = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
car_to_int = None  # N/A
distance_to_int = {miles525: 525, miles550: 550, miles575: 575, miles600: 600}  # in miles
speed_to_int = {speed62: 62, speed69: 69, speed75: 75, speed81: 81}  # in MPH


# Helper functions (for formulating comparison constraints)
def drove_farther_than(var1, var2):
    """
    Formulate the constraint that var1 drove farther than var2.
    """
    return [((d1 == var1) & (d2 == var2)).implies(distance_to_int[d1] > distance_to_int[d2])
            for d1 in distances for d2 in distances]


def drove_exactly_farther_than(var1, var2, diff):
    """
    Formulate the constraint that var1 drove exactly diff miles farther than var2.
    """
    return [((d1 == var1) & (d2 == var2)).implies(distance_to_int[d1] == distance_to_int[d2] + diff)
            for d1 in distances for d2 in distances]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(cars)
m += AllDifferent(distances)
m += AllDifferent(speeds)

# Clue 1: The Leden drove 25 miles farther than the automobile with a high speed of 75 MPH:
m += drove_exactly_farther_than(leden, speed75, 25)

# Clue 2: The Poltris drove 25 miles farther than the automobile with a high speed of 69 MPH:
m += drove_exactly_farther_than(poltris, speed69, 25)

# Clue 3: The Awick drove somewhat less than the automobile with a high speed of 81 MPH:
m += drove_farther_than(speed81, awick)

# Clue 4: The car with a high speed of 69 MPH drove somewhat farther than the automobile with a high speed of 81 MPH:
m += drove_farther_than(speed69, speed81)
