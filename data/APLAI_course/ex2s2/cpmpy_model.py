from cpmpy import *
import json

# Data
num_movies = 9
movies = [
    {"title": "Tarjan of the Jungle", "interval": [4, 13]},
    {"title": "The Four Volume Problem", "interval": [17, 27]},
    {"title": "The President's Algorist", "interval": [1, 10]},
    {"title": "Steiner's Tree", "interval": [12, 18]},
    {"title": "Process Terminated", "interval": [23, 30]},
    {"title": "Halting State", "interval": [9, 16]},
    {"title": "Programming Challenges", "interval": [19, 25]},
    {"title": "Discrete Mathematics", "interval": [2, 7]},
    {"title": "Calculated Bets", "interval": [26, 31]}
]

# Decision variables
# Create decision variables for each movie (1 if the movie is selected, 0 otherwise)
selected_movies = boolvar(shape=num_movies)

# Constraints
m = Model()

# Add constraint for non-overlapping movie schedules

# For each pair of movies, check if the intervals overlap
for i in range(num_movies):
    for j in range(num_movies):
        # Check if the intervals overlap
        if (i != j  # Different movies
                and movies[i]['interval'][1] > movies[j]['interval'][0]  # Movie i ends after movie j starts
                and movies[j]['interval'][1] > movies[i]['interval'][0]  # Movie j ends after movie i starts
        ):
            # If the intervals overlap, the movies cannot be selected together
            m += selected_movies[i] + selected_movies[j] <= 1

# Objective: Maximize the number of selected movies
m.maximize(sum(selected_movies))

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {"selected_movies": [int(selected_movies[i].value()) for i in range(num_movies)]}
    print(json.dumps(solution))
