from cpmpy import *
import json

# Data
num_people = 8
compatible = [  # 1-based indexing
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]

# Decision variables
transplants = boolvar(shape=(num_people, num_people))  # transplants[i][j] is True if i donates to j

# Model setup
m = Model()

# Constraints for the transplant pairs
for i in range(num_people):
    # Anyone who gives a kidney must receive one
    gives_kidney = sum(transplants[i, :]) >= 1
    receives_kidney = sum(transplants[:, i]) >= 1
    m += gives_kidney.implies(receives_kidney)

    # Each person can donate to at most one person and receive from at most one person
    can_donate_once = sum(transplants[i, :]) <= 1
    can_receive_once = sum(transplants[:, i]) <= 1
    m += can_donate_once & can_receive_once

    # Compatibility constraint: if i can't donate to j, then transplants[i][j] must be 0 (adjust for 0-based indexing)
    m += [transplants[i, j] == 0 for j in range(num_people) if j + 1 not in compatible[i]]

# Objective: maximize the number of transplants
m.maximize(sum(transplants))

# Solve the model and print the results in the required format
if m.solve():
    solution = {
        "transplants": [[int(transplants[i, j].value()) for j in range(num_people)] for i in range(num_people)]
    }
    print(json.dumps(solution))
