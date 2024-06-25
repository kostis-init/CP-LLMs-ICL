from cpmpy import *

# Decision variables
# (variables with the same value will correspond to the same triplet of vintage, wine, and type)
# e.g. if annata == 1 and vintage1984 == 1 and chardonnay == 1, then Annata Branco is a 1984 chardonnay
annata, friambliss, luzagueil, zifennwein = wines = intvar(1, 4, shape=4)
vintage1984, vintage1988, vintage1992, vintage1996 = vintages = intvar(1, 4, shape=4)
chardonnay, merlot, pinot_gris, syrah = types = intvar(1, 4, shape=4)

# Integer representation of the decision variables (for comparison constraints)
wine_to_int = None  # N/A
vintage_to_int = {vintage1984: 1984, vintage1988: 1988, vintage1992: 1992, vintage1996: 1996}  # in years
type_to_int = None  # N/A


# Helper functions (for formulating comparison constraints)
def bottled_exactly_after_than(var1, var2, diff):
    """
    Formulate the constraint that var1 was bottled exactly diff years after var2.
    """
    return [((v1 == var1) & (v2 == var2)).implies(vintage_to_int[v1] == vintage_to_int[v2] + diff)
            for v1 in vintages for v2 in vintages]


# Constraints
m = Model()

# All entities are different per category
m += AllDifferent(wines)
m += AllDifferent(vintages)
m += AllDifferent(types)

# Clue 1: The Luzagueil is a chardonnay:
m += luzagueil == chardonnay

# Clue 2: The Annata Branco is either the 1992 wine or the syrah:
m += Xor([
    annata == vintage1992,
    annata == syrah
])

# Clue 3: The Friambliss is a syrah:
m += friambliss == syrah

# Clue 4: Of the pinot gris and the 1984 bottle, one is the Luzagueil and the other is the Zifennwein:
m += Xor([
    (pinot_gris == luzagueil) & (vintage1984 == zifennwein),
    (pinot_gris == zifennwein) & (vintage1984 == luzagueil)
])

# Clue 5: The pinot gris was bottled 4 years after the merlot:
m += bottled_exactly_after_than(pinot_gris, merlot, 4)
