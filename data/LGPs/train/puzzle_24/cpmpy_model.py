from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of runner, price, and pasta)
# e.g. if florence == 1 and price6 == 1 and fettuccine == 1, then Florence paid $6 for fettuccine
florence, margie, suzanne, velma = runners = intvar(1, 4, shape=4)
price6, price7, price8, price9 = prices = intvar(1, 4, shape=4)
fettuccine, fusilli, spaghetti, taglioni = pastas = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
runner_to_int = None  # N/A
price_to_int = {price6: 6, price7: 7, price8: 8, price9: 9}  # in dollars
pasta_to_int = None  # N/A


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
m += AllDifferent(runners)
m += AllDifferent(prices)
m += AllDifferent(pastas)

# Clue 1: Suzanne paid less than Margie:
m += paid_more_than(margie, suzanne)

# Clue 2: Margie paid $7:
m += margie == price7

# Clue 3: The competitor who ordered spaghetti paid 2 dollars more than the competitor who ordered taglioni:
m += paid_exactly_more_than(spaghetti, taglioni, 2)

# Clue 4: Of the runner who paid $9 and the contestant who ordered fettuccine, one was Margie and the other was Velma:
m += Xor([
    (price9 == margie) & (fettuccine == velma),
    (price9 == velma) & (fettuccine == margie)
])

