from cpmpy import *
import json

# Data
num_cows = 25
num_sons = 5
milk_per_cow = list(range(1, num_cows + 1))
cows_per_son = [7, 6, 5, 4, 3]

total_milk = sum(milk_per_cow)  # Total milk produced by all cows
total_milk_per_son = total_milk // num_sons  # Total milk each son should get

# Decision variables
# Each cow is assigned to a son, represented by 0-4
cow_assignments = intvar(0, num_sons - 1, shape=num_cows)

# Constraints
m = Model()

# Each son gets a specific number of cows
for son in range(num_sons):
    m += sum(cow_assignments == son) == cows_per_son[son]

# The total milk production for each son is equal
for son in range(num_sons):
    m += sum(milk_per_cow[i] * (cow_assignments[i] == son) for i in range(num_cows)) == total_milk_per_son

# Solve the model and print the results in the required format
if m.solve():
    solution = {"cow_assignments": [cow_assignments[i].value() for i in range(num_cows)]}
    print(json.dumps(solution))
