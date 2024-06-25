from cpmpy import *
import json

# Data
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]

# Decision variables: 1 if an element is in the subset, 0 otherwise
in_S = boolvar(shape=len(A))
in_T = boolvar(shape=len(A))

# Model setup
m = Model()

# Constraint: sum of elements in S equals sum of elements in T
m += (sum(in_S * A) == sum(in_T * A))

# S and T are disjoint, so there is no element that is in both S and T
m += (sum(in_S * in_T) == 0)

# S and T are non-empty
m += (sum(in_S) > 0)
m += (sum(in_T) > 0)

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"in_S": [int(in_S[i].value()) for i in range(len(A))],
                "in_T": [int(in_T[i].value()) for i in range(len(A))]}
    print(json.dumps(solution))
