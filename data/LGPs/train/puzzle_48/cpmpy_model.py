from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of owner, year, and breed)
# e.g. if anita == 1 and year2006 == 1 and bulldog == 1, then Anita's bulldog won in 2006
anita, elsie, fernando, ginger = owners = intvar(1, 4, shape=4)
year2006, year2007, year2008, year2009 = years = intvar(1, 4, shape=4)
bulldog, dalmatian, irish_setter, maltese = breeds = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
owner_to_int = None  # N/A
year_to_int = {year2006: 2006, year2007: 2007, year2008: 2008, year2009: 2009}  # in years
breed_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def won_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 won exactly diff years after var2.
    """
    return [((y1 == var1) & (y2 == var2)).implies(year_to_int[y1] == year_to_int[y2] + diff)
            for y1 in years for y2 in years]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(owners)
m += AllDifferent(years)
m += AllDifferent(breeds)

# Clue 1: The dalmatian won 1 year after Fernando's canine:
m += won_exactly_after_than(dalmatian, fernando, 1)

# Clue 2: Ginger's dog won 1 year before the irish setter:
m += won_exactly_after_than(irish_setter, ginger, 1)

# Clue 3: Ginger's canine is the bulldog:
m += ginger == bulldog

# Clue 4: The four dogs are the dog that won in 2006, the dalmatian, the bulldog and Elsie's dog:
m += AllDifferent([year2006, dalmatian, bulldog, elsie])

