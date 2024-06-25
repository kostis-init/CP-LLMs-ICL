from cpmpy import *
import json

# Data
total_coins_lost = 100
coin_numbers = [16, 17, 23, 24, 39, 40]

# Decision variables
# The number of bags stolen for each type of coins
bags = intvar(0, total_coins_lost, shape=len(coin_numbers))

# Constraints
m = Model()

# The total number of coins lost is equal to the sum of the coins in the stolen bags
m += sum([bags[i] * coin_numbers[i] for i in range(len(coin_numbers))]) == total_coins_lost

# Solve and print the solution in the specified format
if m.solve():
    solution = {"bags": bags.value().tolist()}
    print(json.dumps(solution))
