from cpmpy import *
import json

range_min = 1
range_max = 100

# Decision variables
a, b, c, d = intvar(range_min, range_max, shape=4)

# Constraints
m = Model()

# Sum of squares of any two numbers is equal to the sum of squares of the other two numbers
m += (a**2 + b**2) == (c**2 + d**2)

# Constraints to ensure all variables are distinct
m += AllDifferent([a, b, c, d])

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
    print(json.dumps(solution))
