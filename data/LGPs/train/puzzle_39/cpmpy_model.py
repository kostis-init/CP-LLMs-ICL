from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same pair of country, gold medals, and silver medals)
# e.g. if dominica == 1 and gold1 == 1 and silver2 == 1, then Dominica won 1 gold medal and 2 silver medals
dominica, jordan, venezuela, zimbabwe = countries = intvar(1, 4, shape=4)
gold1, gold2, gold3, gold4 = gold_medals = intvar(1, 4, shape=4)
silver2, silver5, silver6, silver8 = silver_medals = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
country_to_int = None  # N/A
gold_to_int = {gold1: 1, gold2: 2, gold3: 3, gold4: 4}  # in gold medals
silver_to_int = {silver2: 2, silver5: 5, silver6: 6, silver8: 8}  # in silver medals


# Helper functions (for formulating comparison constraints)
def exactly_fewer_gold_medals_than(var1, var2, diff):
    """
    Formulate the constraint that var1 has exactly diff fewer gold medals than var2.
    """
    return [((g1 == var1) & (g2 == var2)).implies(gold_to_int[g1] == gold_to_int[g2] - diff)
            for g1 in gold_medals for g2 in gold_medals]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(countries)
m += AllDifferent(gold_medals)
m += AllDifferent(silver_medals)

# Clue 1: The team from Venezuela finished with 4 gold medals:
m += venezuela == gold4

# Clue 2: The squad that won 2 gold medals ended with 6 silver medals:
m += gold2 == silver6

# Clue 3: The four teams were the squad from Zimbabwe, the team that won 3 gold medals, the squad that won 6 silver medals and the squad that won 8 silver medals:
m += AllDifferent([zimbabwe, gold3, silver6, silver8])

# Clue 4: The team from Dominica ended the games with 1 fewer gold medal than the squad that won 5 silver medals:
m += exactly_fewer_gold_medals_than(dominica, silver5, 1)
