from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, price, and drink)
# e.g. if delia == 1 and price5 == 1 and americano == 1, then Delia paid $5 for a cafe americano
delia, hope, patricia, wayne = names = intvar(1, 4, shape=4)
price5, price6, price7, price8 = prices = intvar(1, 4, shape=4)
americano, latte, cappuccino, chai = drinks = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
price_to_int = {price5: 5, price6: 6, price7: 7, price8: 8}  # in dollars
drink_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def paid_more_than(var1, var2):
    """
    Formulate the constraint that var1 paid less than var2.
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
m += AllDifferent(names)
m += AllDifferent(prices)
m += AllDifferent(drinks)

# Clue 1: Hope paid less than Delia:
m += paid_more_than(delia, hope)

# Clue 2: Patricia had the cappuccino:
m += patricia == cappuccino

# Clue 3: The one who had the cafe americano paid 1 dollar more than Patricia:
m += paid_exactly_more_than(americano, patricia, 1)

# Clue 4: Hope paid more than the one who had the cafe americano:
m += paid_more_than(hope, americano)

# Clue 5: The one who had the chai tea paid 1 dollar more than the one who had the cafe americano:
m += paid_exactly_more_than(chai, americano, 1)
