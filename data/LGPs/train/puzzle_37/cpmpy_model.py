from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of company, price, and camera)
# e.g. if banion == 1 and price550 == 1 and dm5000 == 1, then Banion makes the DM-5000 that costs $550
banion, dayero, honwa, torvia = companies = intvar(1, 4, shape=4)
price550, price575, price600, price625 = prices = intvar(1, 4, shape=4)
dm5000, fc520, mx827, zenix2c = cameras = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
company_to_int = None  # N/A
price_to_int = {price550: 550, price575: 575, price600: 600, price625: 625}  # in dollars
camera_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def costs_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 costs exactly diff dollars more than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] == price_to_int[p2] + diff)
            for p1 in prices for p2 in prices]


def costs_more_than(var1, var2):
    """
    Formulate the constraint that var1 costs more than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] > price_to_int[p2])
            for p1 in prices for p2 in prices]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(companies)
m += AllDifferent(prices)
m += AllDifferent(cameras)

# Clue 1: The model made by Torvia costs 25 dollars more than the model made by Honwa:
m += costs_exactly_more_than(torvia, honwa, 25)

# Clue 2: The camera made by Honwa is either the Zenix 2C or the MX-827:
m += Xor([
    honwa == zenix2c,
    honwa == mx827
])

# Clue 3: Of the $600 model and the FC-520, one is made by Honwa and the other is made by Dayero:
m += Xor([
    (price600 == honwa) & (fc520 == dayero),
    (price600 == dayero) & (fc520 == honwa)
])

# Clue 4: The Zenix 2C costs less than the FC-520:
m += costs_more_than(fc520, zenix2c)

