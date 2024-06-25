from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of client, masseuse, and price)
# e.g. if aimee == 1 and lynda == 1 and price150 == 1, then aimee's masseuse is lynda and the price is 150
aimee, ginger, freda, hannah = clients = intvar(1, 4, shape=4)
lynda, nancy, teri, whitney = masseuses = intvar(1, 4, shape=4)
price150, price160, price170, price180 = prices = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
client_to_int = None  # N/A
masseuse_to_int = None  # N/A
price_to_int = {price150: 150, price160: 160, price170: 170, price180: 180}  # in dollars


# Helper functions (for formulating comparison constraints)
def paid_more_than(var1, var2):
    """
    Formulate the constraint that var1 paid more than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] > price_to_int[p2])
            for p1 in prices for p2 in prices]


def paid_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 paid exactly $diff more than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] == price_to_int[p2] + diff)
            for p1 in prices for p2 in prices]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(clients)
m += AllDifferent(masseuses)
m += AllDifferent(prices)

# Clue 1: Hannah paid more than Teri's client:
m += paid_more_than(hannah, teri)

# Clue 2: Freda paid 20 dollars more than Lynda's client:
m += paid_exactly_more_than(freda, lynda, 20)

# Clue 3: Hannah paid 10 dollars less than Nancy's client:
m += paid_exactly_more_than(hannah, nancy, -10)

# Clue 4: Nancy's client, Hannah and Ginger were all different clients:
m += AllDifferent([nancy, hannah, ginger])

# Clue 5: Hannah was either the person who paid $180 or Lynda's client:
m += Xor([
    hannah == price180,
    hannah == lynda
])
