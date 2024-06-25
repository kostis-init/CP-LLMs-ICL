from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of winner, price, and order)
# e.g. if daniel == 1 and price250 == 1 and order3rd == 1, then Daniel won the butterfly auctioned 3rd for $250
daniel, gabriel, roland, vincent = winners = intvar(1, 4, shape=4)
price250, price260, price270, price280 = prices = intvar(1, 4, shape=4)
order3rd, order4th, order7th, order8th = orders = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
winner_to_int = None  # N/A
price_to_int = {price250: 250, price260: 260, price270: 270, price280: 280}  # in dollars
order_to_int = {order3rd: 3, order4th: 4, order7th: 7, order8th: 8}  # in auction order


# Helper functions (for formulating comparison constraints)
def sold_for_exactly_less_than(var1, var2, diff):
    """
    Formulate the constraint that var1 sold for exactly diff dollars less than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(price_to_int[p1] == price_to_int[p2] - diff)
            for p1 in prices for p2 in prices]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(winners)
m += AllDifferent(prices)
m += AllDifferent(orders)

# Clue 1: The butterfly that was auctioned 7th sold for 20 dollars less than the insect won by Daniel:
m += sold_for_exactly_less_than(order7th, daniel, 20)

# Clue 2: The four butterflies were the insect that sold for $260, the butterfly that was auctioned 4th, the butterfly that was auctioned 7th and the butterfly won by Roland:
m += AllDifferent([price260, order4th, order7th, roland])

# Clue 3: The butterfly won by Gabriel was the 8th lot:
m += gabriel == order8th

