from cpmpy import *
import json

# Data
n = 8
adjacency_list = [
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
]

# Create a binary decision variable for each node to indicate if it's included in the independent set
nodes = boolvar(shape=n)

# Model setup
m = Model()

# Constraint: No two adjacent nodes can both be in the independent set
for i, neighbors in enumerate(adjacency_list):
    for neighbor in neighbors:
        # Subtract 1 to adjust for 1-based indexing in the data
        neighbor_idx = neighbor - 1
        # Ensure that for every edge, at least one of its endpoints is not in the independent set
        m += ~(nodes[i] & nodes[neighbor_idx])

# Objective: Maximize the number of nodes in the independent set
m.maximize(sum(nodes))

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"nodes": [int(nodes[i].value()) for i in range(n)]}
    print(json.dumps(solution))
