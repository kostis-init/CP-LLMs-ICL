from cpmpy import *
import json

# Decision Variables
a, b, c, d = intvar(1, 9, shape=4)  # a, b, c, d are the four digits of the PIN

# Constraints
m = Model()

m += AllDifferent([a, b, c, d])  # no two digits are the same
m += 10 * c + d == 3 * (10 * a + b)  # cd is 3 times ab
m += 10 * d + a == 2 * (10 * b + c)  # da is 2 times bc

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
    print(json.dumps(solution))