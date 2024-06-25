from llms4cp.util import get_var_names_from_exec_model_str, find_best_match, run_code, CpmpyModelWithVars


def python_code_to_function(python_code: str, function_name: str, var_names: [str],
                            var_names_to_map_to: [str] = None) -> str:
    if '```python' in python_code:
        python_code = python_code.split('```python')[1].split('```')[0]

    # find any import statements and move them out
    import_statements = []
    python_code_lines = python_code.split("\n")
    indexes_to_remove = []
    for i, line in enumerate(python_code_lines):
        if line.startswith("from") or line.startswith("import"):
            import_statements.append(line)
            indexes_to_remove.append(i)
    python_code = "\n".join([line for i, line in enumerate(python_code_lines) if i not in indexes_to_remove])
    import_statements = "\n".join(import_statements)

    # add tab to each line
    python_code = "\n".join(["    " + line for line in python_code.split("\n")])

    if var_names_to_map_to and len(var_names) >= len(var_names_to_map_to):
        # reorder the sequence, so that the variables are in the same order as the var_names_to_map_to most close ones
        # use find_best_match() to find the best match
        vars_new = []
        for var_map_to in var_names_to_map_to:
            best_match = find_best_match(var_map_to, var_names)
            vars_new.append(best_match)
            var_names.remove(best_match)
        var_names = vars_new

    vars_str = ", ".join(var_names)

    return f"""\
{import_statements}
def {function_name}():
    {python_code}
    return CpmpyModelWithVars(m, [{vars_str}])
    """


def check_cpmpy_str_models_equivalence(model1: str, model2: str, remove_after_solve=False) -> bool:
    vars1 = get_var_names_from_exec_model_str(model1)
    vars2 = get_var_names_from_exec_model_str(model2)

    if remove_after_solve:
        # find the line with .solve() and remove this and the following lines
        model1 = model1.split("\n")
        for i, line in enumerate(model1):
            if ".solve()" in line:
                model1 = model1[:i]
                break
        model1 = "\n".join(model1)

        model2 = model2.split("\n")
        for i, line in enumerate(model2):
            if ".solve()" in line:
                model2 = model2[:i]
                break
        model2 = "\n".join(model2)


    f1_str = python_code_to_function(model1, "f1", vars1)
    f2_str = python_code_to_function(model2, "f2", vars2, vars1)

    new_code_to_run = f"""\
from llms4cp.util import models_equivalent
from llms4cp.dataset_classes import CpmpyModelWithVars

{f1_str}

{f2_str}

print(models_equivalent(f1(), f2()))
"""
    output = run_code(new_code_to_run)
    return output.strip().endswith("True")


def check_cpmpy_with_cpmpy_str_model_equivalence(model1: str, model2: CpmpyModelWithVars) -> bool:
    vars1 = get_var_names_from_exec_model_str(model1)

    f1_str = python_code_to_function(model1, "f1", vars1)

    new_code_to_run = f"""\
from llms4cp.util import models_equivalent
from llms4cp.dataset_classes import CpmpyModelWithVars

{f1_str}

print(models_equivalent(f1(), extra_var, 50))
"""
    output = run_code(new_code_to_run, model2)
    return output.strip().endswith("True")


def get_cpmpy_str_per_const_eval(pred: str, label: str, keep_only_last_line: bool = False) -> (int, int):
    vars1 = get_var_names_from_exec_model_str(pred)
    vars2 = get_var_names_from_exec_model_str(label)

    f1_str = python_code_to_function(pred, "f1", vars1)
    f2_str = python_code_to_function(label, "f2", vars2, vars1)

    new_code_to_run = f"""\
from llms4cp.util import declaration_level_evaluation
from llms4cp.dataset_classes import CpmpyModelWithVars

{f1_str}

{f2_str}

print(declaration_level_evaluation(f1(), f2()))
    """
    output = run_code(new_code_to_run)
    if keep_only_last_line:
        return eval(output.strip().split("\n")[-1])
    return eval(output)


def is_objective_equivalent(pred: str, label: str):
    vars1 = get_var_names_from_exec_model_str(pred)
    vars2 = get_var_names_from_exec_model_str(label)

    f1_str = python_code_to_function(pred, "f1", vars1)
    f2_str = python_code_to_function(label, "f2", vars2, vars1)

    new_code_to_run = f"""\
from llms4cp.util import objectives_equivalent
from llms4cp.dataset_classes import CpmpyModelWithVars

{f1_str}

{f2_str}

print(objectives_equivalent(f1(), f2()))
    """
    output = run_code(new_code_to_run)
    return output.strip().endswith("True")



def test_llm_generated_model_equivalence():
    llm_response = """
```python
from cpmpy import Model, intvar, AllDifferent, Xor
import re
# 0. Preliminaries
from cpmpy import *

def add_comparable_constraints(comparable_category_values, comparing_function, var1, var2):
    comparable_category_vars = list(comparable_category_values.keys())
    return [((e1 == var1) & (e2 == var2))
          .implies(comparing_function(comparable_category_values[e1], comparable_category_values[e2]))
          for e1 in comparable_category_vars for e2 in comparable_category_vars]

m = Model()

# 1. Variables (all variables that have the same integer value correspond to the same object)
chianti, port, riesling, shiraz = wines = intvar(1, 4, shape=4)
_24, _25, _26, _27 = prices = intvar(1, 4, shape=4)
isabel, kurt, priscilla, robin = names = intvar(1, 4, shape=4)

# 2. Comparable values (helper dictionaries for comparisons)
prices_values = {_24: 24, _25: 25, _26: 26, _27: 27} # in dollars

# 3. Constraints (all different per category and problem constraints)
m += AllDifferent(wines)
m += AllDifferent(prices)
m += AllDifferent(names)

# The person who had the port paid 1 dollar more than Kurt.
m += add_comparable_constraints(prices_values, lambda var1, var2: var1 == var2 + 1, var1=port, var2=kurt)

# Of the person who paid $25 and the person who paid $24, one was Priscilla and the other had the shiraz.
m += Xor([(priscilla == _25) & (shiraz == _24), (priscilla == _24) & (shiraz == _25)])

# Of the person who paid $27 and Priscilla, one had the chianti and the other had the port.
m += Xor([(priscilla == chianti) & (_27 == port), (priscilla == port) & (_27 == chianti)])

# Isabel paid $25.
m += (isabel == _25)


```
"""

    ground_truth_model = """
```python
# 0. Preliminaries
from cpmpy import *

def add_comparable_constraints(comparable_category_values, comparing_function, var1, var2):
    comparable_category_vars = list(comparable_category_values.keys())
    return [((e1 == var1) & (e2 == var2))
          .implies(comparing_function(comparable_category_values[e1], comparable_category_values[e2]))
          for e1 in comparable_category_vars for e2 in comparable_category_vars]

m = Model()

# 1. Variables (all variables that have the same integer value correspond to the same object)
chianti, port, riesling, shiraz = wines = intvar(1, 4, shape=4)
_24, _25, _26, _27 = prices = intvar(1, 4, shape=4)
isabel, kurt, priscilla, robin = names = intvar(1, 4, shape=4)

# 2. Comparable values (helper dictionaries for comparisons)
prices_values = {_24: 24, _25: 25, _26: 26, _27: 27} # in dollars

# 3. Constraints (all different per category and problem constraints)
m += AllDifferent(wines)
m += AllDifferent(prices)
m += AllDifferent(names)

# The person who had the port paid 1 dollar more than Kurt.
m += add_comparable_constraints(prices_values, lambda var1, var2: var1 == var2 + 1, var1=port, var2=kurt)

# Of the person who paid $25 and the person who paid $24, one was Priscilla and the other had the shiraz.
m += Xor([(priscilla == _25) & (shiraz == _24), (priscilla == _24) & (shiraz == _25)])

# Of the person who paid $27 and Priscilla, one had the chianti and the other had the port.
m += Xor([(priscilla == chianti) & (_27 == port), (priscilla == port) & (_27 == chianti)])

# Isabel paid $25.
m += (isabel == _25)

# The end. You can take it from here.
```
"""

    new_test_pred_1 = '''
from cpmpy import Model, intvar, AllDifferent, Xor

# 1. Decision variables
# (variables with the same value will correspond to the same triplet of name, diet, and pounds lost)
celia, mandy, raymond, tom = names = intvar(1, 4, shape=4)
dairy_free, gluten_free, low_fat, vegan = diets = intvar(1, 4, shape=4)
_3pounds, _5pounds, _7pounds, _9pounds = pounds_lost = intvar(1, 4, shape=4)

# 2. Helpers
# Dictionaries to map variables to their arithmetical values, so that we can add comparison constraints
pounds_to_value = {_3pounds: 3, _5pounds: 5, _7pounds: 7, _9pounds: 9}  # in pounds


# Helper function to add comparison constraints between two variables
def compare_values(var1, var2, comparison, var_to_value):
    all_vars = list(var_to_value.keys())
    return [((e1 == var1) & (e2 == var2)).implies(comparison(var_to_value[e1], var_to_value[e2]))
            for e1 in all_vars for e2 in all_vars]


# 3. Constraints
m = Model()

# All entities are different per category
m += AllDifferent(names)
m += AllDifferent(diets)
m += AllDifferent(pounds_lost)

# Clues:

# Celia used the gluten-free diet.
m += (celia == gluten_free)

# The friend who lost 3 pounds used the low-fat diet.
m += (_3pounds == low_fat)

# Mandy lost 2 fewer pounds than Raymond.
m += compare_values(var1=mandy, var2=raymond, comparison=lambda var1, var2: var1 == var2 - 2, var_to_value=pounds_to_value)

# Mandy lost 4 more pounds than Tom.
m += compare_values(var1=mandy, var2=tom, comparison=lambda var1, var2: var1 == var2 + 4, var_to_value=pounds_to_value)

# The dieter who used the vegan diet is either Mandy or the friend who lost 3 pounds.
m += Xor([mandy == vegan, _3pounds == vegan])    
'''

    new_test_label_1 = '''
# 0. Preliminaries
from cpmpy import *

def add_comparable_constraints(comparable_category_values, comparing_function, var1, var2):
    comparable_category_vars = list(comparable_category_values.keys())
    return [((e1 == var1) & (e2 == var2))
          .implies(comparing_function(comparable_category_values[e1], comparable_category_values[e2]))
          for e1 in comparable_category_vars for e2 in comparable_category_vars]

m = Model()

# 1. Variables (all variables that have the same integer value correspond to the same object)
_3pounds, _5pounds, _7pounds, _9pounds = pounds_lost = intvar(1, 4, shape=4)
dairy_free, gluten_free, low_fat, vegan = diets = intvar(1, 4, shape=4)
celia, mandy, raymond, tom = names = intvar(1, 4, shape=4)

# 2. Comparable values (helper dictionaries for comparisons)
pounds_values = {_3pounds: 3, _5pounds: 5, _7pounds: 7, _9pounds: 9}
diets_values = {dairy_free: "dairy-free", gluten_free: "gluten-free", low_fat: "low-fat", vegan: "vegan"}

# 3. Constraints (all different per category and problem constraints)
m += AllDifferent(pounds_lost)
m += AllDifferent(diets)
m += AllDifferent(names)

# Celia used the gluten-free diet.
m += (celia == gluten_free)

# The friend who lost 3 pounds used the low-fat diet.
m += (low_fat == _3pounds)

# Mandy lost 2 fewer pounds than Raymond.
m += add_comparable_constraints(pounds_values, lambda var1, var2: var1 == var2 - 2, var1=mandy, var2=raymond)

# Mandy lost 4 more pounds than Tom.
m += add_comparable_constraints(pounds_values, lambda var1, var2: var1 == var2 + 4, var1=mandy, var2=tom)

# The dieter who used the vegan diet is either Mandy or the friend who lost 3 pounds.
m += Xor([vegan == mandy, vegan == _3pounds])

# The end. You can take it from here.
'''

    test_pred_2 = '''
from cpmpy import Model, intvar, AllDifferent, Xor

# 1. Decision variables
# (variables with the same value will correspond to the same pair of superhero and person)
criminal_bane, deep_shadow, ultra_hex, wonderman = superheroes = intvar(2007, 2009, shape=4)
gabe_grant, ivor_ingram, matt_minkle, peter_powers = names = intvar(1, 4, shape=4)

# 2. Helpers
# Dictionaries to map variables to their arithmetical values, so that we can add comparison constraints
year_to_value = {2007: 2007, 2008: 2008, 2009: 2009, 2010: 2010}  # in years


# Helper function to add comparison constraints between two variables
def compare_values(var1, var2, comparison, var_to_value):
    all_vars = list(var_to_value.keys())
    return [((e1 == var1) & (e2 == var2)).implies(comparison(var_to_value[e1], var_to_value[e2]))
            for e1 in all_vars for e2 in all_vars]


# 3. Constraints
m = Model()

# All entities are different per category
m += AllDifferent(superheroes)
m += AllDifferent(names)

# Clues:

# Ultra Hex is Gabe Grant.
m += (ultra_hex == gabe_grant)

# Criminal Bane is either the hero who started in 2007 or the superhero who started in 2009.
m += Xor([criminal_bane == 2007, criminal_bane == 2009])

# Peter Powers began sometime before Matt Minkle.
m += compare_values(var1=peter_powers, var2=matt_minkle, comparison=lambda var1, var2: var1 < var2, var_to_value=year_to_value)

# Gabe Grant began 1 year after Wonderman.
m += compare_values(var1=gabe_grant, var2=wonderman, comparison=lambda var1, var2: var1 == var2 + 1, var_to_value=year_to_value)

# The four people are Deep Shadow, the superhero who started in 2007, the hero who started in 2009, and Matt Minkle.
m += AllDifferent([deep_shadow, 2007, 2009, matt_minkle])
'''

    test_label_2 = '''
# 0. Preliminaries
from cpmpy import *

def add_comparable_constraints(comparable_category_values, comparing_function, var1, var2):
    comparable_category_vars = list(comparable_category_values.keys())
    return [((e1 == var1) & (e2 == var2))
          .implies(comparing_function(comparable_category_values[e1], comparable_category_values[e2]))
          for e1 in comparable_category_vars for e2 in comparable_category_vars]

m = Model()

# 1. Variables (all variables that have the same integer value correspond to the same object)
_2007, _2008, _2009, _2010 = years = intvar(1, 4, shape=4)
criminal_bane, deep_shadow, ultra_hex, wonderman = superheroes = intvar(1, 4, shape=4)
gabe_grant, ivor_ingram, matt_minkle, peter_powers = names = intvar(1, 4, shape=4)

# 2. Comparable values (helper dictionaries for comparisons)
years_values = {_2007: 2007, _2008: 2008, _2009: 2009, _2010: 2010} # in years

# 3. Constraints (all different per category and problem constraints)
m += AllDifferent(superheroes)
m += AllDifferent(years)
m += AllDifferent(names)

# Ultra Hex is Gabe Grant.
m += (ultra_hex == gabe_grant)

# Criminal Bane is either the hero who started in 2007 or the superhero who started in 2009.
m += Xor([criminal_bane == _2007, criminal_bane == _2009])

# Peter Powers began sometime before Matt Minkle.
m += add_comparable_constraints(years_values, lambda var1, var2: var1 < var2, var1=peter_powers, var2=matt_minkle)

# Gabe Grant began 1 year after Wonderman.
m += add_comparable_constraints(years_values, lambda var1, var2: var1 == var2 + 1, var1=gabe_grant, var2=wonderman)

# The four people are Deep Shadow, the superhero who started in 2007, the hero who started in 2009 and Matt Minkle.
m += AllDifferent([deep_shadow, _2007, _2009, matt_minkle])

# The end. You can take it from here.
'''

    test_pred_3 = '''
```python

from cpmpy import Model, intvar

# Decision Variables
Mangos = intvar(0, 999999999)  # Number of mangos sold
Guavas = intvar(0, 999999999)  # Number of guavas sold

# Constraints
m = Model()

# The total cost of mangos and guavas should not exceed $20000:
m += 5 * Mangos + 3 * Guavas <= 20000
# At least 100 mangos are sold:
m += Mangos >= 100
# At most 150 mangos are sold:
m += Mangos <= 150
# The number of guavas sold is at most a third of the mangos sold:
m += Guavas <= Mangos / 3

# Objective
# Maximize profit (3 dollars profit per mango, 4 dollars profit per guava):
m.maximize(3 * Mangos + 4 * Guavas)

```
'''
    test_label_3 = '''
from cpmpy import Model, intvar

# Decision Variables
Mangos = intvar(0, 999999999)  # Number of mangos sold
Guavas = intvar(0, 999999999)  # Number of guavas sold

# Constraints
m = Model()

# The total cost of mangos and guavas should not exceed $20000:
# Cost of mango is $5 and guava is $3
m += 5 * Mangos + 3 * Guavas <= 20000
# At least 100 mangos but at the most 150 are sold each month:
m += Mangos >= 100
m += Mangos <= 150
# The number of guavas sold is at most a third of the mangos sold:
m += 3 * Guavas <= Mangos

# Objective
# Maximize profit (Profit per mango is $3 and per guava is $4):
m.maximize(3 * Mangos + 4 * Guavas)

'''

    run_code(test_label_3)

    check_cpmpy_str_models_equivalence(llm_response, ground_truth_model)
    print('====== CHECK PER CONSTRAINT ======')
    per_const = get_cpmpy_str_per_const_eval(llm_response, ground_truth_model)
    print('falses:' + str(per_const[0]))
    print('total_declarations:' + str(per_const[1]))

    print('====== CHECK NEW TEST ======')
    check_cpmpy_str_models_equivalence(new_test_pred_1, new_test_label_1)
    per_const = get_cpmpy_str_per_const_eval(new_test_pred_1, new_test_label_1)
    print('falses:' + str(per_const[0]))
    print('total_declarations:' + str(per_const[1]))

    print('====== CHECK NEW TEST 2 ======')
    check_cpmpy_str_models_equivalence(test_label_2, test_pred_2)
    per_const = get_cpmpy_str_per_const_eval(test_pred_2, test_label_2)
    print('falses:' + str(per_const[0]) + ' total_declarations:' + str(per_const[1]))

    print('====== CHECK NEW TEST 3 ======')
    check_cpmpy_str_models_equivalence(test_pred_3, test_label_3)
    per_const = get_cpmpy_str_per_const_eval(test_pred_3, test_label_3)
    is_obj = is_objective_equivalent(test_pred_3, test_label_3)
    print('falses:' + str(per_const[0]) + ' total_declarations:' + str(per_const[1]))
    print('objective equivalent: ' + str(is_obj))


if __name__ == "__main__":
    test_llm_generated_model_equivalence()
