from cpmpy import *
import json

# Data
num_edges = 9
graph = [
    [3, 1],
    [3, 6],
    [3, 4],
    [6, 4],
    [6, 1],
    [1, 5],
    [1, 4],
    [4, 5],
    [4, 2]
]
nodes = ["Belgium", "Denmark", "France", "Germany", "Netherlands", "Luxembourg"]

# Model

# Decision Variables
colors = intvar(1, len(nodes), shape=len(nodes))  # the colour assigned to each country

# Constraints
m = Model()

# Two neighbouring countries cannot have the same colour
for i, j in graph:
    # Python uses 0-based indexing, but the countries are 1-based, so we need to subtract 1 from the indices
    m += colors[i - 1] != colors[j - 1]

# Objective
# Find a colouring that minimizes the number of colours used
m.minimize(max(colors))

# Solve and print the solution in the specified format
if m.solve():
    solution = {"colors": colors.value().tolist()}
    print(json.dumps(solution))
