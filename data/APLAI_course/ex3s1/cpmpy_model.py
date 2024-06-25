from cpmpy import *
import json

# Decision variables
# We model the ages, children, countries, and stories as integer variables with values from 1 to 5.
age3, age5, age7, age8, age10 = ages = intvar(1, 5, shape=5)
bernice, carl, debby, sammy, ted = children = intvar(1, 5, shape=5)
ethiopia, kazakhstan, lithuania, morocco, yemen = countries = intvar(1, 5, shape=5)
burning_bush, captivity, moses_youth, passover, ten_commandments = stories = intvar(1, 5, shape=5)

# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(ages)
m += AllDifferent(children)
m += AllDifferent(countries)
m += AllDifferent(stories)

# Debby’s family is from Lithuania.
m += debby == lithuania

# The child who told the story of the Passover is two years older than Bernice.
# So, we will add constraints for all possible pairs of ages to enforce this relationship.
age_to_int = {age3: 3, age5: 5, age7: 7, age8: 8, age10: 10}
m += [((a1 == passover) & (a2 == bernice)).implies(age_to_int[a1] == age_to_int[a2] + 2)
      for a1 in ages for a2 in ages]

# The child whose family is from Yemen is younger than the child from the Ethiopian family.
m += [((a1 == yemen) & (a2 == ethiopia)).implies(age_to_int[a1] < age_to_int[a2])
      for a1 in ages for a2 in ages]

# The child from the Moroccan family is three years older than Ted.
m += [((a1 == morocco) & (a2 == ted)).implies(age_to_int[a1] == age_to_int[a2] + 3)
      for a1 in ages for a2 in ages]

# Sammy is three years older than the child who told the story of Moses’s youth in the house of the Pharaoh.
m += [((a1 == sammy) & (a2 == moses_youth)).implies(age_to_int[a1] == age_to_int[a2] + 3)
      for a1 in ages for a2 in ages]

# Solve the model and print the solution in the specified format
if m.solve():
    solution = {
        "ages": ages.value().tolist(),
        "children": children.value().tolist(),
        "countries": countries.value().tolist(),
        "stories": stories.value().tolist()
    }
    print(json.dumps(solution))
