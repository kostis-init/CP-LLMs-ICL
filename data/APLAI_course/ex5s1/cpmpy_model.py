from cpmpy import *
import numpy as np
import json

# Data
total_price = 711  # total price in cents
num_items = 4

# Decision variables (prices are considered in cents)
prices = intvar(1, total_price, shape=num_items)

# Constraints
m = Model()

# The sum of the prices in cents is equal to the total price in cents
m += sum(prices) == total_price

# The product of the prices should equal to the scaled total price in cents (to account for the multiplication)
m += np.prod(prices) == total_price * (100 ** (num_items - 1))

# Solve the model and print the results in the required format
if m.solve():
    solution = {"prices": prices.value().tolist()}
    print(json.dumps(solution))
