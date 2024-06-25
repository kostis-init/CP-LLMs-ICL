from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of company, pieces, and theme)
# e.g. if buralde == 1 and pieces250 == 1 and autumn_leaves == 1, then Buralde made a 250-piece puzzle with an autumn leaves theme
buralde, denlend, irycia, kimsight = companies = intvar(1, 4, shape=4)
pieces250, pieces500, pieces750, pieces1000 = pieces = intvar(1, 4, shape=4)
autumn_leaves, coral_reef, outer_space, rustic_village = themes = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
company_to_int = None  # N/A
pieces_to_int = {pieces250: 250, pieces500: 500, pieces750: 750, pieces1000: 1000}  # in pieces
theme_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def has_more_pieces_than(var1, var2):
    """
    Formulate the constraint that var1 has more pieces than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(pieces_to_int[p1] > pieces_to_int[p2])
            for p1 in pieces for p2 in pieces]


def has_exactly_more_pieces_than(var1, var2, diff):
    """
    Formulate the constraint that var1 has exactly diff more pieces than var2.
    """
    return [((p1 == var1) & (p2 == var2)).implies(pieces_to_int[p1] == pieces_to_int[p2] + diff)
            for p1 in pieces for p2 in pieces]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(companies)
m += AllDifferent(pieces)
m += AllDifferent(themes)

# Clue 1: The puzzle with the autumn leaves theme has somewhat more than the jigsaw puzzle with the rustic village theme:
m += has_more_pieces_than(autumn_leaves, rustic_village)

# Clue 2: The four puzzles are the puzzle made by Buralde, the jigsaw puzzle with the rustic village theme, the puzzle with the autumn leaves theme and the puzzle with 1000 pieces:
m += AllDifferent([buralde, rustic_village, autumn_leaves, pieces1000])

# Clue 3: The jigsaw puzzle made by Buralde has the outer space theme:
m += buralde == outer_space

# Clue 4: The jigsaw puzzle made by Denlend has somewhat fewer than the jigsaw puzzle with the outer space theme:
m += has_more_pieces_than(outer_space, denlend)

# Clue 5: The jigsaw puzzle made by Kimsight has 250 more pieces than the puzzle made by Denlend:
m += has_exactly_more_pieces_than(kimsight, denlend, 250)

