from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of name, price, and drink)
# e.g. if angela == 1 and price4 == 1 and cream_soda == 1, then Angela paid $4 for cream soda
angela, edmund, homer, irene = names = intvar(1, 4, shape=4)
price4, price5, price6, price7 = prices = intvar(1, 4, shape=4)
cream_soda, iced_tea, root_beer, water = drinks = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
name_to_int = None  # N/A
price_to_int = {price4: 4, price5: 5, price6: 6, price7: 7}  # in dollars
drink_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def paid_more_than(var1, var2):
    """
    Formulate the constraint that var1 paid more than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] > price_to_int[p2])
            for p1 in prices for p2 in prices]


def paid_exactly_more_than(var1, var2, diff):
    """
    Formulate the constraint that var1 paid exactly diff dollars more than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] == price_to_int[p2] + diff)
            for p1 in prices for p2 in prices]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(prices)
m += AllDifferent(drinks)

# Clue 1: Edmund paid 1 dollar less than the one who got the water:
m += paid_exactly_more_than(water, edmund, 1)

# Clue 2: The diner who paid $4 had the iced tea:
m += price4 == iced_tea

# Clue 3: Angela paid more than the one who got the cream soda:
m += paid_more_than(angela, cream_soda)

# Clue 4: The diner who paid $5 was either the one who got the cream soda or the one who got the iced tea:
m += Xor([
    price5 == cream_soda,
    price5 == iced_tea
])

# Clue 5: The four diners were the diner who paid $5, the one who got the iced tea, the one who got the root beer and Irene:
m += AllDifferent([price5, iced_tea, root_beer, irene])

