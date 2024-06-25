from cpmpy import *
import json

# Decision Variables
B = intvar(1, 5)  # Baker
C = intvar(1, 5)  # Cooper
F = intvar(1, 5)  # Fletcher
M = intvar(1, 5)  # Miller
S = intvar(1, 5)  # Smith

# Constraints
m = Model()

m += B != 5  # Baker does not live on the fifth floor
m += C != 1  # Cooper does not live on the first floor
m += (F != 5) & (F != 1)  # Fletcher does not live on either the fifth or the first floor
m += M > C  # Miller lives on a higher floor than does Cooper
m += abs(S - F) != 1  # Smith does not live on a floor adjacent to Fletcher
m += abs(F - C) != 1  # Fletcher does not live on a floor adjacent to Cooper
m += AllDifferent([B, C, F, M, S])  # They all live on different floors

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"B": B.value(), "C": C.value(), "F": F.value(), "M": M.value(), "S": S.value()}
    print(json.dumps(solution))

