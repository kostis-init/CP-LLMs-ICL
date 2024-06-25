import math
import sys
import io
import contextlib

from cpmpy import intvar, Model, AllDifferent, Xor
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from llms4cp.dataset_classes import CpmpyModelWithVars
from llms4cp.in_context_config import *

from langchain.prompts.example_selector import SemanticSimilarityExampleSelector, MaxMarginalRelevanceExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import cpmpy
import random

import difflib
import re


def run_code(code: str, extra_var=None) -> str:
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    # Create a new namespace (all variable defined in the 'code' will be stored here)
    namespace = {}

    if extra_var:
        # add the extra var to the namespace dictionary
        namespace['extra_var'] = extra_var

    # String for error messages
    err_msg = ''

    try:
        with contextlib.redirect_stdout(new_stdout):
            exec(code, namespace)

    except Exception as e:
        err_msg = str(e)

    finally:
        sys.stdout = old_stdout

    return new_stdout.getvalue() + err_msg  # Return the console output


def find_best_match(name, name_set):
    """
    Finds the best match for a given name in a set of names, considering exact, prefix, substring, and similarity matches.

    :param name: The name to match.
    :param name_set: A list of names to search in.
    :return: The most similar name from the set.
    """

    def numeric_value(s):
        numbers = re.findall(r'\d+', s)
        return int(numbers[0]) if numbers else None

    def similarity(a, b):
        text_ratio = difflib.SequenceMatcher(None, a, b).ratio()
        num_a, num_b = numeric_value(a), numeric_value(b)
        num_ratio = 1.0 if num_a == num_b else 0.0 if num_a is None or num_b is None else 1 - abs(num_a - num_b) / max(
            num_a, num_b)
        return text_ratio * 0.5 + num_ratio * 0.5

    # First, check for exact matches
    if name in name_set:
        return name

    best_match = None
    highest_similarity = 0.0

    # Check for prefix and substring matches, prioritizing longer matches
    for candidate in name_set:
        if candidate.startswith(name) or name.startswith(candidate):
            return candidate  # Return immediately if a clear prefix match is found

        part_similarity = max(similarity(part, candidate) for part in name.split('_'))
        if part_similarity > highest_similarity:
            highest_similarity = part_similarity
            best_match = candidate

    # If no prefix or exact match is found, look for the best similarity match
    if not best_match:
        for candidate in name_set:
            sim = similarity(name, candidate)
            if sim > highest_similarity:
                highest_similarity = sim
                best_match = candidate

    return best_match


def get_var_names_from_exec_model_str(exec_str):
    # find variable names, by finding the lines that contain the intvar word, and until the = sign
    var_lines = [line.split("=")[0].strip() for line in exec_str.split("\n") if "intvar(" in line or "boolvar(" in line]
    # get var names by splitting the line by the comma
    var_names_ = [line.split(",") for line in var_lines]
    # flatten the list
    var_names = [var.strip() for sublist in var_names_ for var in sublist]

    # find category variable names, after the first and before the second = sign
    # category_var_names = [line.split("=")[1].strip() for line in exec_str.split("\n") if "intvar(" in line]

    return var_names


def execute_and_get_solution(executable_model: str) -> [[str]]:
    if '```python' in executable_model:
        exec_str = executable_model.split("```python")[1].split("```")[0]
    else:
        exec_str = executable_model

    var_names = get_var_names_from_exec_model_str(exec_str)

    # find the model variable name
    model_var_name = [line.split("=")[0].strip() for line in exec_str.split("\n") if "Model(" in line][0]

    #     print(f'[{aimee.value()}, {ginger.value()}, {freda.value()}, {hannah.value()}, {price150.value()}, {price160.value()}, {price170.value()}, {price180.value()}, {lynda.value()}, {nancy.value()}, {teri.value()}, {whitney.value()}]')
    vars_with_values_str = ''
    for v in var_names:
        vars_with_values_str += '{' + v + '.value()},'

    exec_str += f'''
if not {model_var_name}.solve(time_limit=10):
    print('UNSAT')
else:
    print(f'[{vars_with_values_str}]')
'''

    prefix = """
from cpmpy import *

"""

    output = run_code(prefix + exec_str)

    if 'UNSAT' in output:
        return None

    values = eval(output)

    if None in values:
        return None

    final = []
    for i in range(max(values)):
        final.append([])

    for var_, val_ in zip(var_names, values):
        final[val_ - 1].append(var_)

    return final


def get_number_of_constraints(cpmpy_model_str: str) -> int:
    # count the number of lines that contain the += sign and start with m +=
    return len([line for line in cpmpy_model_str.split("\n") if "+=" in line and line.strip().startswith("m")])


def cpmpy_model_is_unsat(executable_model: str) -> bool:
    if '```python' in executable_model:
        exec_str = executable_model.split("```python")[1].split("```")[0]
    else:
        exec_str = executable_model

    exec_str += '\nprint(f"Model Solved: {m.solve(time_limit=10)}, Status: {m.status()}")\n'

    return 'false' in run_code(exec_str).lower()


def format_final_executable(executable_model: str, candidate_sol: [[str]]) -> str:
    if '```python' in executable_model:
        exec_str = executable_model.split("```python")[1].split("```")[0]
    else:
        exec_str = executable_model

    var_names = get_var_names_from_exec_model_str(exec_str)

    # construct the given_solution dictionary
    exec_str += "\ngiven_solution = {"
    for i, sol_triplet in enumerate(candidate_sol):
        for var_sol in sol_triplet:
            var_name = find_best_match(var_sol, var_names)
            exec_str += f'{var_name}: {i + 1}, '
    exec_str = exec_str[:-2]  # remove the last comma and space
    exec_str += "}\n"
    exec_str += """
m += [var == val for var, val in given_solution.items()]
print(f"Model Solved: {m.solve(time_limit=10)}, Status: {m.status()}")
"""

    prefix = """
from cpmpy import *

"""

    return prefix + exec_str


def choose_example_selector(dataset):
    examples = [{"question": p.question,
                 "ner": p.entities_as_str,
                 "pseudo_model": p.pseudo_model,
                 "cpmpy_code": p.cpmpy_code_wrapped,
                 'direct_solution': p.direct_solution} for p in dataset]



    if NUM_EXAMPLES == 0 or EXAMPLES_SELECTOR == "rand" or EXAMPLES_SELECTOR == "static":
        return None
    elif EXAMPLES_SELECTOR == "mmr":
        return MaxMarginalRelevanceExampleSelector.from_examples(examples, OpenAIEmbeddings(), Chroma, k=NUM_EXAMPLES,
                                                                 fetch_k=40)
    elif EXAMPLES_SELECTOR == "sim":
        return SemanticSimilarityExampleSelector.from_examples(examples, OpenAIEmbeddings(), Chroma, k=NUM_EXAMPLES)
    elif EXAMPLES_SELECTOR == "lsrd":
        return SemanticSimilarityExampleSelector.from_examples(examples, OpenAIEmbeddings(), Chroma, k=1)
    else:
        raise ValueError(f"Unknown example selector: {EXAMPLES_SELECTOR}")


def get_examples_for_context(example_selector, input_vars, dataset):
    if NUM_EXAMPLES == 0:
        return []
    elif EXAMPLES_SELECTOR == "static" or EXAMPLES_SELECTOR == "rand":
        return [{
            "question": p.question,
            "ner": p.entities_as_str,
            "pseudo_model": p.pseudo_model,
            "cpmpy_code": p.cpmpy_code_wrapped,
            'direct_solution': p.direct_solution
        } for p in dataset[:NUM_EXAMPLES]]
    elif EXAMPLES_SELECTOR == "lsrd":
        selected_examples = [{
            "question": p.question,
            "ner": p.entities_as_str,
            "pseudo_model": p.pseudo_model,
            "cpmpy_code": p.cpmpy_code_wrapped,
            'direct_solution': p.direct_solution
        } for p in dataset[:NUM_EXAMPLES - 1]]
        selected_examples.append(example_selector.select_examples(input_vars)[0])
        return selected_examples
    else:
        selected_examples = example_selector.select_examples(input_vars)
        if REVERSED_ORDER_ICL:
            # reverse the order of the examples so that the last one is the most relevant
            selected_examples = selected_examples[::-1]
        return selected_examples


def flatten(const):
    if not isinstance(const, (list, tuple)):
        yield const
        return

    for el in const:
        if isinstance(el, list):
            yield from flatten(el)
        else:
            yield el


def limited_permutations(lst, limit=100):
    """Generate up to `limit` unique permutations of `lst`."""
    seen = set()
    list_len = len(lst)

    # first give the initial list
    yield lst
    seen.add(tuple(lst))

    while len(seen) < limit:
        # Randomly shuffle the list to simulate a new permutation
        random.shuffle(lst)
        perm_tuple = tuple(lst)
        if perm_tuple not in seen:
            seen.add(perm_tuple)
            yield list(perm_tuple)
        # To prevent infinite loops in cases where `limit` exceeds the total possible permutations
        if len(seen) == math.factorial(list_len):
            break


def declaration_level_evaluation(pred: CpmpyModelWithVars, gt: CpmpyModelWithVars):
    fps, fns, total_declarations = 0, max(len(gt.model.constraints) - len(pred.model.constraints), 0), len(
        gt.model.constraints)

    # go with default mapping only, depends on the order that vars were added to the CpmpyModelWithVars
    _mapping = True
    for var1, var2 in list(zip(pred.vars_, gt.vars_)):
        _mapping &= (var1 == var2)

    label_constraints_used_indexes = []
    for pred1 in pred.model.constraints:
        found = False
        for idx, label1 in enumerate(gt.model.constraints):
            if idx in label_constraints_used_indexes:
                continue
            constraints_equivalent = models_equivalent(CpmpyModelWithVars(cpmpy.Model(pred1), pred.vars_),
                                                       CpmpyModelWithVars(cpmpy.Model(label1), gt.vars_))
            if constraints_equivalent:
                found = True
                label_constraints_used_indexes.append(idx)
                break
        if not found:
            fps += 1

    return min(fps + fns, total_declarations), total_declarations


def objectives_equivalent(m1: CpmpyModelWithVars, m2: CpmpyModelWithVars) -> bool:
    # If both models have no objective function, they are equivalent
    if not m1.model.objective_ and not m2.model.objective_:
        return True

    # If one model has an objective function and the other does not, they are not equivalent
    if not m1.model.objective_ or not m2.model.objective_:
        return False

    obj1 = m1.model.objective_
    obj2 = m2.model.objective_

    if m1.model.objective_is_min != m2.model.objective_is_min:
        obj2 = -obj2

    _mapping = True
    for var1, var2 in list(zip(m1.vars_, m2.vars_)):
        _mapping &= (var1 == var2)

    return not Model(_mapping & (obj1 != obj2)).solve(time_limit=10)


def models_equivalent(m1: CpmpyModelWithVars, m2: CpmpyModelWithVars, perm_limit=0) -> bool:
    """
    Check if two CPMpy models are equivalent. This means that m1 entails m2 and m2 entails m1.
    So, we map all combinations of variables between the two and check if the models are equivalent.
    Note: The objective function is not considered in this method.
    :param m1: The first CPMpy model
    :param m2: The second CPMpy model
    :param perm_limit: The maximum number of permutations to check for variable mappings
    :return: True if the models are equivalent, False otherwise
    """

    vars1, vars2 = m1.vars_, m2.vars_
    if len(vars1) != len(vars2):
        # make them the same length
        if len(vars1) > len(vars2):
            vars1 = vars1[:len(vars2)]
        else:
            vars2 = vars2[:len(vars1)]

    for perm in limited_permutations(vars2, limit=perm_limit):
        _mapping = True
        for var1, var2 in list(zip(vars1, perm)):
            _mapping &= (var1 == var2)

        _m1 = True
        for c in m1.model.constraints:
            for cc in list(flatten(c)):
                _m1 &= cc

        _m2 = True
        for c in m2.model.constraints:
            for cc in list(flatten(c)):
                _m2 &= cc

        final = cpmpy.Model(_mapping & ((_m1 & ~_m2) | (~_m1 & _m2)))

        if not final.solve(time_limit=10):
            return True

    return False


def modeltest1():
    from cpmpy import Model, intvar

    # Decision Variables
    SledDogTrips = intvar(0, 999999999)  # Number of sled dog trips
    TruckTrips = intvar(0, 999999999)  # Number of truck trips

    # Constraints
    m = Model()

    # The budget for transportation is at most $1000:
    m += 50 * SledDogTrips + 100 * TruckTrips <= 1000
    # The number of sled dog trips must be less than the number of truck trips:
    m += SledDogTrips < TruckTrips

    # Objective
    # Maximize the number of fish that can be transported (100 fish per sled dog trip, 300 fish per truck trip):
    m.maximize(100 * SledDogTrips + 300 * TruckTrips)

    return CpmpyModelWithVars(m, [SledDogTrips, TruckTrips])


def modeltest2():
    from cpmpy import Model, intvar

    # Decision Variables
    SledDogTrips = intvar(0, 999999999)  # Number of sled dog trips
    TruckTrips = intvar(0, 999999999)  # Number of truck trips

    # Constraints
    m = Model()

    # The budget for transportation is at most $1000:
    m += 50.0 * SledDogTrips + 100.0 * TruckTrips <= 1000.0
    # The number of sled dog trips must be less than the number of truck trips:
    m += 1 * SledDogTrips - 1.0 * TruckTrips < 0

    # Objective
    # Maximize the number of fish that can be transported (100 fish per sled dog trip, 300 fish per truck trip):
    m.minimize(-100.0 * SledDogTrips - 300.0 * TruckTrips)

    return CpmpyModelWithVars(m, [SledDogTrips, TruckTrips])


def f1():
    # 1. Decision variables
    # (variables with the same value will correspond to the same triplet of wine, price, and name)
    chianti, port, riesling, shiraz = wines = intvar(1, 4, shape=4)
    price24, price25, price26, price27 = prices = intvar(1, 4, shape=4)
    isabel, kurt, priscilla, robin = names = intvar(1, 4, shape=4)

    # 2. Helpers
    # Dictionaries to map variables to their arithmetical values, so that we can add comparison constraints
    price_to_value = {price24: 24, price25: 25, price26: 26, price27: 27}  # in dollars

    # Helper function to add comparison constraints between two variables
    def compare_values(var1, var2, comparison, var_to_value):
        all_vars = list(var_to_value.keys())
        return [((e1 == var1) & (e2 == var2)).implies(comparison(var_to_value[e1], var_to_value[e2]))
                for e1 in all_vars for e2 in all_vars]

    # 3. Constraints
    m = Model()

    # All entities are different per category
    m += AllDifferent(wines)
    m += AllDifferent(prices)
    m += AllDifferent(names)

    # Clues:

    # The person who had the port paid 1 dollar more than Kurt.
    m += compare_values(var1=port, var2=kurt, comparison=lambda var1, var2: var1 == var2 + 1,
                        var_to_value=price_to_value)

    # Of the person who paid $25 and the person who paid $24, one was Priscilla and the other had the shiraz.
    m += Xor([(priscilla == price25) & (shiraz == price24), (priscilla == price24) & (shiraz == price25)])

    # Of the person who paid $27 and Priscilla, one had the chianti and the other had the port.
    m += Xor([priscilla == price27, priscilla == chianti])

    # Isabel paid $25.
    m += (isabel == price25)

    return CpmpyModelWithVars(m, [chianti, port, riesling, shiraz, price24, price25, price26, price27, isabel, kurt,
                                  priscilla, robin])


def f2():
    # 0. Preliminaries

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
    prices_values = {_24: 24, _25: 25, _26: 26, _27: 27}  # in dollars

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

    return CpmpyModelWithVars(m, [chianti, port, riesling, shiraz, _24, _25, _26, _27, isabel, kurt, priscilla, robin])


def test():
    vars1 = intvar(1, 4, shape=10)
    vars2 = intvar(1, 4, shape=10)
    m1 = Model()
    m1 += vars1[0] - 1 == 0
    m2 = Model()
    m2 += vars2[0] == 1
    mm1 = CpmpyModelWithVars(m1, vars1)
    mm2 = CpmpyModelWithVars(m2, vars2)
    assert models_equivalent(mm1, mm2) == True
    assert models_equivalent(modeltest1(), modeltest2()) == True
    assert models_equivalent(f1(), f2()) == True
    print(declaration_level_evaluation(f1(), f2()))


def test_execute_and_get_solution():
    executable_model = """
from cpmpy import Model, intvar, AllDifferent, Xor

# 1. Decision variables
# (variables with the same value will correspond to the same triplet of duration, rower, and start point)
days184, days195, days206, days217 = durations = intvar(1, 4, shape=4)
antonio, dana, hilda, walter = rowers = intvar(1, 4, shape=4)
bodega_bay, cayucos, pescadero, pismo_beach = start_points = intvar(1, 4, shape=4)

# 2. Helpers
# Dictionaries to map variables to their arithmetical values, so that we can add comparison constraints
duration_to_value = {days184: 184, days195: 195, days206: 206, days217: 217}  # in days


# Helper function to add comparison constraints between two variables
def compare_values(var1, var2, comparison, var_to_value):
    all_vars = list(var_to_value.keys())
    return [((e1 == var1) & (e2 == var2)).implies(comparison(var_to_value[e1], var_to_value[e2]))
            for e1 in all_vars for e2 in all_vars]


# 3. Constraints
m = Model()

# All entities are different per category
m += AllDifferent(durations)
m += AllDifferent(rowers)
m += AllDifferent(start_points)

# Clues:

# The athlete who traveled for 195 days started from Pescadero.
m += (days195 == pescadero)

# Of Dana and the athlete who traveled for 184 days, one started from Cayucos and the other started from Bodega Bay.
m += Xor([(dana == cayucos) & (days184 == bodega_bay), (dana == bodega_bay) & (days184 == cayucos)])

# Hilda finished in 217 days.
m += (hilda == days217)

# Walter finished 11 days before the athlete who started from Cayucos.
m += compare_values(var1=walter, var2=cayucos, comparison=lambda var1, var2: var1 == var2 - 11, var_to_value=duration_to_value)  
    """

    gt = """
# 0. Preliminaries
from cpmpy import *

def add_comparable_constraints(comparable_category_values, comparing_function, var1, var2):
    comparable_category_vars = list(comparable_category_values.keys())
    return [((e1 == var1) & (e2 == var2))
          .implies(comparing_function(comparable_category_values[e1], comparable_category_values[e2]))
          for e1 in comparable_category_vars for e2 in comparable_category_vars]

m = Model()

# 1. Variables (all variables that have the same integer value correspond to the same object)
_184days, _195days, _206days, _217days = durations = intvar(1, 4, shape=4)
antonio, dana, hilda, walter = rowers = intvar(1, 4, shape=4)
bodega_bay, cayucos, pescadero, pismo_beach = start_points = intvar(1, 4, shape=4)

# 2. Comparable values (helper dictionaries for comparisons)
durations_values = {_184days: 184, _195days: 195, _206days: 206, _217days: 217} # in days

# 3. Constraints (all different per category and problem constraints)
m += AllDifferent(durations)
m += AllDifferent(rowers)
m += AllDifferent(start_points)

# The athlete who traveled for 195 days started from Pescadero.
m += _195days == pescadero

# Of Dana and the athlete who traveled for 184 days, one started from Cayucos and the other from Bodega Bay.
m += Xor([(dana == cayucos) & (_184days == bodega_bay), (dana == bodega_bay) & (_184days == cayucos)])

# Hilda finished in 217 days.
m += hilda == _217days

# Walter finished 11 days before the athlete who started from Cayucos.
m += add_comparable_constraints(durations_values, lambda var1, var2: var1 == var2 - 11, var1=walter, var2=cayucos)

# The end. You can take it from here.
"""

    predicted_solution = execute_and_get_solution(executable_model)
    print(predicted_solution)
    to_run = format_final_executable(gt, predicted_solution)
    print(to_run)


def test_find_best_match():
    print(find_best_match('days195', ['_184days', '_195days', '_206days', '_217days']) == '_195days')
    print(find_best_match('days206', ['_184', '_195', '_206', '_217']) == '_206')
    print(find_best_match('score63', ['_42', '_49', '_56', '_63']) == '_63')
    print(find_best_match('age32', ['_14', '_32', '_50', '_68']) == '_32')
    print(find_best_match('price1000', ['_500', '_750', '_1000', '_1250']) == '_1000')
    print(find_best_match('price750', ['_500', '_750', '_1000', '_1250']) == '_750')
    print(find_best_match('age75', ['_69million', '_75million', '_78million', '_85million']) == '_75million')

    print(find_best_match('benny baron', ['benny', 'edith', 'hal', 'iva']) == 'benny')
    print(find_best_match('hal harrison',
                          ['benny', 'edith', 'hal', 'iva', 'aug4', 'aug5', 'aug6', 'aug7', 'islesboro', 'long_barn',
                           'tarzana', 'zearing']) == 'hal')
    print(find_best_match('iva ingram', ['benny', 'edith', 'hal', 'iva']) == 'iva')
    print(find_best_match('august 6', ['aug4', 'aug5', 'aug6', 'aug7']) == 'aug6')
    print(find_best_match('august 7', ['aug4', 'aug5', 'aug6', 'aug7']) == 'aug7')
    print(find_best_match('long barn', ['islesboro', 'long_barn', 'tarzana', 'zearing']) == 'long_barn')

    print(find_best_match('hal', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                  'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                  'zearing']) == 'hal harrison')
    print(find_best_match('benny', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                    'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                    'zearing']) == 'benny baron')
    print(find_best_match('edith', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                    'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                    'zearing']) == 'edith estes')
    print(find_best_match('iva', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                  'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                  'zearing']) == 'iva ingram')
    print(find_best_match('aug4', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                   'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                   'zearing']) == 'august 4')
    print(find_best_match('aug5', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                   'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                   'zearing']) == 'august 5')
    print(find_best_match('aug6', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                   'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                   'zearing']) == 'august 6')
    print(find_best_match('aug7', ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                                   'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana',
                                   'zearing']) == 'august 7')
    print(find_best_match('islesboro',
                          ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                           'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana', 'zearing']) == 'islesboro')
    print(find_best_match('long barn',
                          ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                           'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana', 'zearing']) == 'long barn')
    print(find_best_match('tarzana',
                          ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                           'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana', 'zearing']) == 'tarzana')
    print(find_best_match('zearing',
                          ['benny baron', 'edith estes', 'hal harrison', 'iva ingram', 'august 4', 'august 5',
                           'august 6', 'august 7', 'islesboro', 'long barn', 'tarzana', 'zearing']) == 'zearing')

    all_label = ['angel', 'charlie', 'gracie', 'merlin', '_102inches', '_106inches', '_110inches', '_114inches',
                 '_8years', '_9years', '_10years', '_11years']
    all_pred = ['angel', 'charlie', 'gracie', 'merlin', 'wingspan102', 'wingspan106', 'wingspan110', 'wingspan114',
                'age8', 'age9', 'age10', 'age11']

    print(find_best_match('wingspan110', all_label) == '_110inches')
    print(find_best_match('age8', all_label) == '_8years')
    print(find_best_match('age10', all_label) == '_10years')

    all_label = ['ethel_street', 'fred_lane', 'juniper_lane', 'quince_street', 'al_anderson', 'cal_craft',
                 'ed_erickson',
                 'hal_hamilton', 'april', 'may', 'june', 'july']
    all_pred = ['ethel', 'fred', 'juniper', 'quince', 'al', 'cal', 'ed', 'hal', 'april', 'may', 'june', 'july']

    print(find_best_match('ethel', all_label) == 'ethel_street')
    print(find_best_match('cal', all_label) == 'cal_craft')
    print(find_best_match('june', all_label) == 'june')
    print(find_best_match('july', all_label) == 'july')
    print(find_best_match('ethel_street', all_pred) == 'ethel')
    print(find_best_match('cal_craft', all_pred) == 'cal')
    print(find_best_match('june', all_pred) == 'june')
    print(find_best_match('july', all_pred) == 'july')

    # labels
    # january, february, march, april = months = intvar(1, 4, shape=4)
    # essita_cbt, haramarui_lv, kuchiwa_w10, rodim_rexit = names = intvar(1, 4, shape=4)
    # direct_drive, fusor, tokamak, z_pinch = types = intvar(1, 4, shape=4)
    # pred
    # essita, haramarui, kuchiwa, rodim = names = intvar(1, 4, shape=4)
    # january, february, march, april = months = intvar(1, 4, shape=4)
    # direct_drive, fusor, tokamak, z_pinch = types = intvar(1, 4, shape=4)
    labels = ['january', 'february', 'march', 'april', 'essita_cbt', 'haramarui_lv', 'kuchiwa_w10', 'rodim_rexit',
              'direct_drive', 'fusor', 'tokamak', 'z_pinch']
    print(find_best_match('essita', labels) == 'essita_cbt')
    print(find_best_match('haramarui', labels) == 'haramarui_lv')
    print(find_best_match('kuchiwa', labels) == 'kuchiwa_w10')
    print(find_best_match('rodim', labels) == 'rodim_rexit')

    labels = ['klein', 'underwood', 'walls', 'zimmerman', '_6', '_7', '_8', '_9', 'checkers', 'comets', 'ice_hogs',
              'wolverines']
    print(find_best_match('goals6', labels) == '_6')
    print(find_best_match('goals7', labels) == '_7')
    print(find_best_match('goals8', labels) == '_8')
    print(find_best_match('goals9', labels) == '_9')

    labels = ['_110', '_150', '_190', '_230']
    print(find_best_match('cap110', labels) == '_110')
    print(find_best_match('cap150', labels) == '_150')
    print(find_best_match('cap190', labels) == '_190')
    print(find_best_match('cap230', labels) == '_230')

    labels = ['_3pounds', '_5pounds', '_7pounds', '_9pounds', 'dairy_free', 'gluten_free', 'low_fat', 'vegan', 'celia',
              'mandy', 'raymond', 'tom']
    print(find_best_match('pounds3', labels) == '_3pounds')
    print(find_best_match('pounds5', labels) == '_5pounds')
    print(find_best_match('pounds7', labels) == '_7pounds')
    print(find_best_match('pounds9', labels) == '_9pounds')
    print(find_best_match('dairy_free', labels) == 'dairy_free')
    print(find_best_match('gluten_free', labels) == 'gluten_free')
    print(find_best_match('low_fat', labels) == 'low_fat')
    print(find_best_match('vegan', labels) == 'vegan')
    print(find_best_match('celia', labels) == 'celia')
    print(find_best_match('mandy', labels) == 'mandy')
    print(find_best_match('raymond', labels) == 'raymond')
    print(find_best_match('tom', labels) == 'tom')

    # price45, price60, price75, price90 = prices = intvar(1, 4, shape=4)
    # alejandro, faye, irma, phillip = winners = intvar(1, 4, shape=4)
    # atlas, emperor, grayling, peacock = butterflies = intvar(1, 4, shape=4)

    # _45, _60, _75, _90 = prices = intvar(1, 4, shape=4)
    # alejandro, faye, irma, phillip = winners = intvar(1, 4, shape=4)
    # atlas, emperor, grayling, peacock = butterflies = intvar(1, 4, shape=4)
    labels = ['_45', '_60', '_75', '_90', 'alejandro', 'faye', 'irma', 'phillip', 'atlas', 'emperor', 'grayling',
              'peacock']
    print(find_best_match('price45', labels) == '_45')
    print(find_best_match('price60', labels) == '_60')
    print(find_best_match('price75', labels) == '_75')
    print(find_best_match('price90', labels) == '_90')


def test_obj():
    m1 = Model()
    m2 = Model()

    x1, y1 = intvar(0, 10), intvar(0, 10)
    x2, y2 = intvar(0, 10), intvar(0, 10)

    m1 += x1 + y1 <= 10

    m1.minimize(x1 + 4 * y1)
    m2.minimize(1 * x2 + 4 * y2)

    print(objectives_equivalent(CpmpyModelWithVars(m1, [x1, y1]), CpmpyModelWithVars(m2, [x2, y2])) == True)

    m1 = Model()
    m2 = Model()

    x1, y1 = intvar(0, 10), intvar(0, 10)
    x2, y2 = intvar(0, 10), intvar(0, 10)

    m1 += x1 + y1 <= 10

    m1.minimize(x1 + 4 * y1)
    m2.minimize(0.999999 * x2 + 2 * y2)

    print(objectives_equivalent(CpmpyModelWithVars(m1, [x1, y1]), CpmpyModelWithVars(m2, [x2, y2])) == False)

    m1 = Model()
    m2 = Model()

    x1, y1 = intvar(0, 10), intvar(0, 10)
    x2, y2 = intvar(0, 10), intvar(0, 10)

    m1 += x1 + y1 <= 10

    m2.minimize(0.999999 * x2 + 2 * y2)

    print(objectives_equivalent(CpmpyModelWithVars(m1, [x1, y1]), CpmpyModelWithVars(m2, [x2, y2])) == False)

    m1 = Model()
    m2 = Model()

    x1, y1 = intvar(0, 10), intvar(0, 10)
    x2, y2 = intvar(0, 10), intvar(0, 10)

    print(objectives_equivalent(CpmpyModelWithVars(m1, [x1, y1]), CpmpyModelWithVars(m2, [x2, y2])) == True)

    m1 = Model()
    m2 = Model()

    x1, y1 = intvar(0, 10), intvar(0, 10)
    x2, y2 = intvar(0, 10), intvar(0, 10)

    m1 += x1 + y1 <= 10

    m1.minimize(-1 * x1 + 4.2 * y1)
    m2.minimize(4.2 * y2 - 1 * x2)

    print(objectives_equivalent(CpmpyModelWithVars(m1, [x1, y1]), CpmpyModelWithVars(m2, [x2, y2])) == True)

    m1 = Model()
    m2 = Model()

    x1, y1 = intvar(0, 10), intvar(0, 10)
    x2, y2 = intvar(0, 10), intvar(0, 10)

    m1 += x1 + y1 <= 10

    m1.minimize(-1 * x1 + 4.2 * y1)
    m2.maximize(-4.2 * y2 + 1 * x2)

    print(objectives_equivalent(CpmpyModelWithVars(m1, [x1, y1]), CpmpyModelWithVars(m2, [x2, y2])) == True)


if __name__ == "__main__":
    test()
    test_obj()
    test_execute_and_get_solution()
    test_find_best_match()
