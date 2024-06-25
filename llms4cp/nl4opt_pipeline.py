from typing import Dict
import numpy as np
import re
from datetime import datetime
from jsonlines import jsonlines

from llms4cp.data_reader import read_nl4opt_test_data
from llms4cp.dataset_classes import Nl4optProblem, CanonicalFormulation, CpmpyModelWithVars
from llms4cp.in_context_config import *
from llms4cp.call_llms import call_llm
from llms4cp.lgps_cpmpy_model_equivalence import get_cpmpy_str_per_const_eval, check_cpmpy_str_models_equivalence, \
    is_objective_equivalent
from llms4cp.util import choose_example_selector, find_best_match, run_code, get_var_names_from_exec_model_str, \
    get_examples_for_context
import cpmpy

NL4OPT_PROBLEMS_TRAIN = []
with jsonlines.open('data/nl4opt/train_new_with_rag_and_ner.jsonl') as reader_train:
    for line in reader_train.iter():
        problem = Nl4optProblem(
            line['document'],
            line['order_mapping'],
            line['cpmpy_code'] if 'cpmpy_code' in line else "MISSING CPMpy CODE",
            line['solution'],
            line['canonical'],
            line['pseudo_model'] if 'pseudo_model' in line else "MISSING PSEUDO MODEL",
            line['direct_solution'] if 'direct_solution' in line else "MISSING DIRECT SOLUTION",
            line['entities'] if 'entities' in line else []
        )
        NL4OPT_PROBLEMS_TRAIN.append(problem)
if EXAMPLES_SELECTOR == "rand" or EXAMPLES_SELECTOR == "lsrd":
    np.random.seed(42)
    np.random.shuffle(NL4OPT_PROBLEMS_TRAIN)


def get_cpmpy_model_from_canonical(canonical: CanonicalFormulation,
                                   var_labels_with_om: Dict = None) -> CpmpyModelWithVars:
    # Variables
    num_vars = len(canonical.objective)

    vars_ = []
    if var_labels_with_om is None:
        vars_ = cpmpy.intvar(0, 999999999, shape=num_vars)
    else:
        # sort the keys based on the values in order_mapping
        var_labels = sorted(var_labels_with_om, key=var_labels_with_om.get)
        for var in var_labels:
            vars_.append(cpmpy.intvar(0, 999999999, name=var))

    # Constraints
    model_ = cpmpy.Model()
    for constraint in canonical.constraints:
        coeffs = constraint[:-1]
        rhs = constraint[-1]
        if rhs == -1e-06:
            model_ += sum([coeff * var for coeff, var in zip(coeffs, vars_)]) < 0
        else:
            model_ += sum([coeff * var for coeff, var in zip(coeffs, vars_)]) <= rhs

    # Objective (minimize)
    coeffs = canonical.objective
    model_.minimize(sum([coeff * var for coeff, var in zip(coeffs, vars_)]))

    return CpmpyModelWithVars(model_, vars_)


def is_pred_solution_correct(pred_solution: Dict, order_mapping, canonical: CanonicalFormulation) -> bool:
    num_vars = len(canonical.objective)
    model_ = get_cpmpy_model_from_canonical(canonical).model

    solved = model_.solve()
    if not solved:
        return pred_solution is None
    if pred_solution is None or len(pred_solution) != num_vars:
        return False

    # if we add the pred solution as constraint the model should be satisfied
    new_model = get_cpmpy_model_from_canonical(canonical, order_mapping)
    for i in range(num_vars):
        var_name = list(order_mapping.keys())[list(order_mapping.values()).index(i)]
        pred_key = find_best_match(var_name, pred_solution.keys())
        if pred_key is None or pred_solution[pred_key] is None:
            continue
        new_model.model += new_model.vars_[i] == pred_solution[pred_key]

    if not new_model.model.solve():
        return False

    # the final objective value of the model should be the same as the one in the pred_solution
    true_obj_val = model_.objective_value()

    pred_obj = 0
    for i in range(num_vars):
        # find the first key with value i in order mapping
        var_name = list(order_mapping.keys())[list(order_mapping.values()).index(i)]
        pred_key = find_best_match(var_name, pred_solution.keys())
        pred_obj += float(pred_solution[pred_key]) * canonical.objective[i]

    return true_obj_val == pred_obj


def pipeline_direct_solution():
    """
    In this method, the LLM directly produces a rationale and final solution.
    """
    dataset = read_nl4opt_test_data()
    wrong, total = 0, 0
    errors = 0
    to_log = []

    for i, (document, order_mapping, canonical, _, _) in enumerate(dataset):
        if i >= LIMIT:
            break

        try:
            text = 'The given problem is as follows:\n' + document + '\n\n' + SYSTEM_MESSAGE_NL4OPT_SOLVE
            messages, answer = call_llm(get_examples_for_context(None, None, NL4OPT_PROBLEMS_TRAIN), text,
                                        system_message=SYSTEM_MESSAGE_NL4OPT_SOLVE, method='DIRECT')
            print(f'ANSWER:\n{answer}\n')
            if 'UNSATISFIABLE' in answer:
                pred_solution = None
            else:
                # extract the json object after ### FINAL ANSWER and convert to dictionary
                pred_solution = eval(re.split(r"### FINAL ANSWER:", answer)[1].strip())

            result = is_pred_solution_correct(pred_solution, order_mapping, canonical)
            print(f'Correct: {result}')
            if not result:
                wrong += 1
            total += 1

            print("-------------------------------------------------------------")
            to_log.append((document, order_mapping, canonical, answer))
        except Exception as e:
            print("An exception occurred:")
            print(e)
            errors += 1
            to_log.append((document, order_mapping, canonical, "Error:\n" + str(e)))

    print(f"Wrong: {wrong}, Total: {total}")
    print(f"Accuracy: {100.0 - (wrong * 100.0 / total)}%")
    print(f"Errors: {errors}")

    path_to_results = f'results/nl4opt/direct/{NUM_EXAMPLES}-shot/{EXAMPLES_SELECTOR}/{MODEL}'
    if not os.path.exists(path_to_results):
        os.makedirs(path_to_results)
    with open(f'{path_to_results}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Wrong: {wrong}, Total: {total}\n")
        f.write(f"Accuracy: {100.0 - (wrong * 100.0 / total)}%\n")
        f.write(f"Errors: {errors}\n")
        f.write('---------------------------------------------------------------------------------------------\n\n')
        for item in to_log:
            for entry in item:
                f.write(f'{entry}\n')
            f.write('---------------------------------------------------------------------------------------------\n\n')


def pipeline_cpmpy_model(with_pseudo=False, with_ner=False):
    """
    In this method, the LLM produces a CPMpy model.
    We also note the problem-level and constraint-level accuracy.
    """
    dataset = read_nl4opt_test_data()

    const_wrong, const_total, const_err = 0, 0, 0
    prob_wrong, prob_err = 0, 0
    sol_wrong, sol_err = 0, 0

    to_log = []

    method = 'CPMPY'
    if with_ner:
        method = 'NER'
    elif with_pseudo:
        method = 'PSEUDO'

    example_selector = choose_example_selector(NL4OPT_PROBLEMS_TRAIN)

    for i, (document, order_mapping, canonical, entities, true_cpmpy_code) in enumerate(dataset):
        print(f"Problem {i + 1} / {len(dataset)}")

        # if i != 37:
        #     continue

        if i >= LIMIT:
            break

        pseudo_model_answer = 'N/A'
        question = document
        input_vars = {"question": question}
        if with_ner:
            entities_as_str = ''
            for entity in entities:
                entities_as_str += entity['entity_group'] + ' (' + str(entity['start']) + '-' + str(
                    entity['end']) + '): ' + entity['word'] + '\n'
            input_vars["ner"] = entities_as_str
            question += '\n' + entities_as_str

        try:
            if with_pseudo:
                messages, pseudo_model_answer = call_llm(
                    get_examples_for_context(example_selector, input_vars, NL4OPT_PROBLEMS_TRAIN), question,
                    system_message=SYSTEM_MESSAGE_PSEUDO_NL4OPT, method=method, step='GEN_PSEUDO')
                print(f'ANSWER (PSEUDO MODEL):\n{pseudo_model_answer}')
                input_vars["pseudo_model"] = pseudo_model_answer
                question += '\n' + pseudo_model_answer

            messages, orig_answer = call_llm(
                get_examples_for_context(example_selector, input_vars, NL4OPT_PROBLEMS_TRAIN), question,
                system_message=SYSTEM_MESSAGE_CPMPY_NL4OPT, method=method, step='GEN_CPMPY')
            print(f'ANSWER:\n{orig_answer}\n')
        except Exception as e:
            print("Error while calling LLM:")
            print(e)
            continue

        # SOLUTION EVALUATION: pred solution should satisfy ground truth model,
        # so it should give the same objective value and satisfy the constraints
        try:
            sol_c = eval_predicted_model_on_solution_direct(canonical, order_mapping, orig_answer)

            if not sol_c:
                sol_log = 'False'
                sol_wrong += 1
                print("Solution given by predicted model is wrong")
            else:
                sol_log = 'True'
        except Exception as e:
            print("Error when trying to check solution from predicted model: ")
            print(e)
            sol_log = 'Error: ' + str(e)
            sol_err += 1

        # DECLARATION EVALUATION
        const_total += len(canonical.constraints) + 1
        is_obj_correct = False
        try:
            wrong_consts, total_consts = get_cpmpy_str_per_const_eval(orig_answer, true_cpmpy_code)
            is_obj_correct = is_objective_equivalent(orig_answer, true_cpmpy_code)
            const_wrong += wrong_consts
            if not is_obj_correct:
                const_wrong += 1
            const_log = f'Wrong: {wrong_consts}, Total: {total_consts}, Is objective correct: {is_obj_correct}'
            print(const_log)
        except Exception as e:
            print("Error in constraint evaluation: ")
            print(e)
            const_log = 'Error: ' + str(e)
            const_err += len(canonical.constraints) + 1

        # MODEL EVALUATION
        try:
            if check_cpmpy_str_models_equivalence(orig_answer, true_cpmpy_code) and is_obj_correct:
                print("Models are equivalent")
                mod_log = 'True'
            else:
                print("Models are not equivalent")
                prob_wrong += 1
                mod_log = 'False'
        except Exception as e:
            print("Error in model evaluation: ")
            print(e)
            mod_log = 'Error: ' + str(e)
            prob_err += 1

        print("-------------------------------------------------------------")
        to_log.append((document, pseudo_model_answer, orig_answer, sol_log, mod_log, const_log))

    total = len(dataset)
    sol_acc = 100.0 - ((sol_wrong + sol_err) * 100.0 / total)
    const_acc = 100.0 - ((const_wrong + const_err) * 100.0 / const_total)
    mod_acc = 100.0 - ((prob_wrong + prob_err) * 100.0 / total)

    print(f"Solution accuracy: {sol_acc}%")
    print(f'Constraint accuracy: {const_acc}%')
    print(f'Model accuracy: {mod_acc}%')
    print(f'Wrong solutions: {sol_wrong}, error solutions: {sol_err}')
    print(f'Wrong constraints: {const_wrong}, error constraints: {const_err}, total: {const_total}')
    print(f'Wrong models: {prob_wrong}, error models: {prob_err}')

    pref = 'pseudo_model' if with_pseudo else 'cpmpy_model'
    pref = 'ner' if with_ner else pref

    if EXAMPLES_SELECTOR == 'mmr' or EXAMPLES_SELECTOR == 'sim':
        examples_pref = 'reversed_' if REVERSED_ORDER_ICL else 'normal_'
        examples_pref += EXAMPLES_SELECTOR
    else:
        examples_pref = EXAMPLES_SELECTOR

    path_to_results = f'results/nl4opt/{pref}/{NUM_EXAMPLES}-shot/{examples_pref}/{MODEL}'
    if not os.path.exists(path_to_results):
        os.makedirs(path_to_results)
    with open(f'{path_to_results}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Solution accuracy: {sol_acc}%\n")
        f.write(f'Constraint accuracy: {const_acc}%\n')
        f.write(f'Model accuracy: {mod_acc}%\n\n')
        f.write(f'Wrong solutions: {sol_wrong}, error solutions: {sol_err}\n')
        f.write(f'Wrong constraints: {const_wrong}, error constraints: {const_err}, total: {const_total}\n')
        f.write(f'Wrong models: {prob_wrong}, error models: {prob_err}\n')
        f.write('---------------------------------------------------------------------------------------------\n\n')
        for item in to_log:
            for entry in item:
                f.write(f'{entry}\n')
            f.write('---------------------------------------------------------------------------------------------\n\n')


def eval_predicted_model_on_solution_direct(canonical, order_mapping, executable_model):
    if '```python' in executable_model:
        exec_str = executable_model.split("```python")[1].split("```")[0]
    else:
        exec_str = executable_model

    # find the model variable name
    model_var_name = [line.split("=")[0].strip() for line in exec_str.split("\n") if "Model(" in line][0]
    var_names = get_var_names_from_exec_model_str(exec_str)

    # add the solve and print statements
    vars_with_values_str = ''
    for v in var_names:
        vars_with_values_str += '{' + v + '.value()},'
    exec_str += f'''
if not {model_var_name}.solve():
    print('UNSAT')
else:
    print(f'[{vars_with_values_str}]')
'''

    prefix = """
from cpmpy import *

    """

    output = run_code(prefix + exec_str)

    # parse the output to dict
    if 'UNSAT' in output or None in eval(output):
        bb_sol = None
    else:
        values = eval(output)
        bb_sol = {var_: val_ for var_, val_ in zip(var_names, values)}
    # compare with the true solution
    return is_pred_solution_correct(bb_sol, order_mapping, canonical)


def run_nl4opt(method):
    if method == 'DIRECT':
        print("Running Direct Solution pipeline for NL4OPT...")
        pipeline_direct_solution()
    elif method == 'CPMPY':
        print("Running CPMPy Model pipeline for NL4OPT...")
        pipeline_cpmpy_model(with_pseudo=False, with_ner=False)  # CPMpy
    elif method == 'PSEUDO':
        print("Running Pseudo Model pipeline for NL4OPT...")
        pipeline_cpmpy_model(with_pseudo=True, with_ner=False)  # Pseudo and Cpmpy
    elif method == 'NER':
        print("Running NER pipeline for NL4OPT...")
        pipeline_cpmpy_model(with_pseudo=True, with_ner=True)  # NER and Pseudo and Cpmpy
    else:
        raise ValueError(f"Unknown method: {method}")
