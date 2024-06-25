from cpmpy import *
import json

# Data
total_people = 13
num_males = 4

# Decision variable: 0 for male, 1 for female
sequence = boolvar(shape=total_people)

# Constraints
m = Model()

# Ensure exactly number of males and females
m += [sum(sequence) == total_people - num_males]

# Add constraints for the ratio at each point in the sequence
for i in range(1, total_people):
    total_females_so_far = sum(sequence[:i])
    total_males_so_far = i - sum(sequence[:i])
    # Number of females to males is no greater than 7/3, or 3 times the females is less than or equal to 7 times the males
    m += (3 * total_females_so_far) <= (7 * total_males_so_far)

# Solve and print the solution in the specified format
if m.solve():
    solution = {"sequence": [int(sequence[i].value()) for i in range(total_people)]}
    print(json.dumps(solution))
