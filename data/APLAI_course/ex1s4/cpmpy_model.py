from cpmpy import *
import json

# Data
n = 4  # size of the magic square
magic_sum = n * (n**2 + 1) // 2  # sum of each row, column and diagonal

# Decision Variables
square = intvar(1, n ** 2, shape=(n, n))  # the magic square

# Constraints
m = Model()

# All numbers in the magic square must be different
m += AllDifferent(square)

# The sum of the numbers in each row must be equal to the magic sum
for i in range(n):
    m += sum(square[i, :]) == magic_sum

# The sum of the numbers in each column must be equal to the magic sum
for j in range(n):
    m += sum(square[:, j]) == magic_sum

# The sum of the numbers in the main diagonal must be equal to the magic sum
m += sum(square[i, i] for i in range(n)) == magic_sum

# The sum of the numbers in the other diagonal must be equal to the magic sum
m += sum(square[i, n - 1 - i] for i in range(n)) == magic_sum

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"square": square.value().tolist()}
    print(json.dumps(solution))
