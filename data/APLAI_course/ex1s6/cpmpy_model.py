from cpmpy import *
import json

# Data
amount = 199  # amount of money to give to Bob
n = 6  # number of types of coins
types_of_coins = [1, 2, 5, 10, 25, 50]  # value of each type of coin
available_coins = [20, 10, 15, 8, 4, 2]  # number of available coins of each type

# Decision Variables
# Create a variable for each type of coin, with each variable's domain set to [0, available_coins[i]]
coin_counts = [intvar(0, available_coins[i]) for i in range(n)]

# Constraints
m = Model()

# The sum of the coins given to Bob must be equal to the amount of money to give him
m += sum(coin_counts[i] * types_of_coins[i] for i in range(n)) == amount

# Objective: Minimize the total number of coins given to Bob
m.minimize(sum(coin_counts))

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"coin_counts": [coin_counts[i].value() for i in range(n)]}
    print(json.dumps(solution))
