from cpmpy import *
import json

# Data
num_gates = 5

# Decision Variables
apples = intvar(0, 1_000_000, shape=num_gates + 1)  # the number of apples before each gate plus after the last gate

# Constraints
m = Model()

# The boy is left with no apples after giving the apple to the girl, so he has 1 apple after the last gate.
m += apples[-1] == 1

# At each guard, the boy gives half of his apples, plus one.
for i in range(1, num_gates + 1):
    has_before = apples[i - 1]
    has_after = apples[i]
    m += has_before == 2 * (has_after + 1)

# Solve and print the solution in the specified format
if m.solve():
    solution = {"apples": apples.value().tolist()}
    print(json.dumps(solution))
