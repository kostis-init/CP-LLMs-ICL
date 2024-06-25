import os
from datetime import datetime

import numpy as np
import json

from llms4cp.call_llms import call_llm
from llms4cp.data_reader import read_aplai_data
from llms4cp.in_context_config import LIMIT, SYSTEM_MESSAGE_APLAI_SOLVE, EXAMPLES_SELECTOR, SYSTEM_MESSAGE_PSEUDO_APLAI, \
    SYSTEM_MESSAGE_CPMPY_APLAI, REVERSED_ORDER_ICL, NUM_EXAMPLES, MODEL
from llms4cp.lgps_cpmpy_model_equivalence import check_cpmpy_str_models_equivalence, get_cpmpy_str_per_const_eval
from llms4cp.util import get_examples_for_context, choose_example_selector, execute_and_get_solution, \
    cpmpy_model_is_unsat, run_code, format_final_executable, get_var_names_from_exec_model_str, \
    get_number_of_constraints

DATASET = read_aplai_data()
if EXAMPLES_SELECTOR == "rand" or EXAMPLES_SELECTOR == "lsrd":
    np.random.seed(42)
    np.random.shuffle(DATASET)


def pipeline_direct_solution():

    wrong, total = 0, 0
    errors = 0
    to_log = []

    for i, problem in enumerate(DATASET):

        dataset_without_current = [x for j, x in enumerate(DATASET) if j != i]

        if i >= LIMIT:
            break

        try:
            text = 'The given problem is as follows:\n' + problem.description + '\n\n' + SYSTEM_MESSAGE_APLAI_SOLVE
            messages, answer = call_llm(
                get_examples_for_context(None, None, dataset_without_current),
                text, system_message=SYSTEM_MESSAGE_APLAI_SOLVE, method='DIRECT')
            print(f'ANSWER:\n{answer}\n')
        except Exception as e:
            print("Error while calling LLM:" + str(e))
            # Try again with the same problem
            i -= 1
            continue

        try:

            lines = answer.splitlines()

            # ### FINAL ANSWER: {"mappings": [{"Cornick", "January", "Techtrin"}, {"Dreadco", "February", "Ubersplore"}, {"Worul", "March", "Permias"}, {"Foltron", "April", "Rubicorp"}]}
            # find the line that contains ### FINAL ANSWER
            answer_line = None
            for line in lines:
                if "final answer" in line.lower():
                    answer_line = line

            if answer_line is None:
                print("No final answer found")
                errors += 1
                to_log.append((text, answer, 'No final answer found'))
                continue

            # find the json object
            pred_answer_line = answer_line.split("### FINAL ANSWER: ")[1]

            # predicted solution is a json object
            predicted_solution = json.loads(pred_answer_line)
            # get keys
            keys = list(predicted_solution.keys())
            # add each key as a constraint in code

            _consts_to_add = ''
            for key in keys:
                _consts_to_add += f'm += {key} == {predicted_solution[key]}\n'

            new_code = problem.cpmpy_code + '\n' + _consts_to_add + '\n'
            new_code += 'print(f"Model Solved: {m.solve(time_limit=10)}, Status: {m.status()}")\n'
            code_output = run_code(new_code)
            sol_2 = "Model Solved: True" in code_output
            if sol_2:
                print("Solution 2 successful")
                sol_2_log = 'True'
            else:
                print("Solution 2 failed")
                wrong += 1
                sol_2_log = 'False'
        except Exception as e:
            print("Error when trying to check solution from predicted model: " + str(e))
            sol_2_log = 'Error when trying to check solution from predicted model: ' + str(e)
            errors += 1

        to_log.append((text, answer, sol_2_log))

    total = len(DATASET)
    sol_2_acc = 100 * (total - wrong - errors) / total

    print(f"Total problems: {total}")
    print(f"Solution accuracy: {sol_2_acc:.2f}%")
    print()
    print(f"Problems with wrong solution: {wrong}")
    print(f"Errors: {errors}")

    # log to file
    path_to_results = f'results/APLAI/direct/{NUM_EXAMPLES}-shot/{EXAMPLES_SELECTOR}/{MODEL}'
    if not os.path.exists(path_to_results):
        os.makedirs(path_to_results)
    with open(f'{path_to_results}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Solution accuracy: {sol_2_acc}%\n")
        f.write(f'Wrong solutions: {wrong}, total: {total}\n')
        f.write(f'Errors: {errors}\n')
        f.write('---------------------------------------------------------------------------------------------\n\n')
        for item in to_log:
            f.write(f"Question: {item[0]}\n")
            f.write(f"Predicted answer: {item[1]}\n")
            f.write(f"Solution log: {item[2]}\n")
            f.write('---------------------------------------------------------------------------------------------\n\n')



def pipeline_cpmpy_model(with_pseudo=False, with_ner=False):
    const_wrong, const_total, const_err = 0, 0, 0
    prob_wrong, prob_err = 0, 0
    sol_wrong, sol_err = 0, 0
    sol_2_wrong, sol_2_err = 0, 0
    sol_final_correct = 0

    to_log = []

    method = 'CPMPY'
    if with_ner:
        method = 'NER'
    elif with_pseudo:
        method = 'PSEUDO'

    example_selector = choose_example_selector(DATASET)

    i = 0
    while i < len(DATASET):
        print(f"Problem {i + 1} / {len(DATASET)}")
        prob = DATASET[i]

        dataset_without_current = [x for j, x in enumerate(DATASET) if j != i]

        # clear example selector db
        if example_selector is not None:
            example_selector.vectorstore.delete(example_selector.vectorstore._collection.get()['ids'])

        example_selector = choose_example_selector(dataset_without_current)

        if i >= LIMIT:
            break
        i += 1

        question = prob.question
        pseudo_model_answer = 'N/A'
        input_vars = {"question": question}
        if with_ner:
            input_vars["ner"] = prob.entities_as_str
            question += '\n' + prob.entities_as_str

        try:
            if with_pseudo:
                messages, pseudo_model_answer = call_llm(
                    get_examples_for_context(example_selector, input_vars, dataset_without_current),
                    question, system_message=SYSTEM_MESSAGE_PSEUDO_APLAI, method=method, step='GEN_PSEUDO')
                print(f'ANSWER (BLUEPRINT MODEL):\n{pseudo_model_answer}')
                input_vars["pseudo_model"] = pseudo_model_answer
                question += '\n' + pseudo_model_answer

            # var_names = get_var_names_from_exec_model_str(prob.cpmpy_code)
            # question += '\nPlease use the following variable names in your code: ' + ', '.join(var_names)

            messages, cpmpy_answer = call_llm(
                get_examples_for_context(example_selector, input_vars, dataset_without_current),
                question, system_message=SYSTEM_MESSAGE_CPMPY_APLAI, method=method, step='GEN_CPMPY')

            print(f'CPMPY ANSWER:\n{cpmpy_answer}\n')

        except Exception as e:
            print("Error while calling LLM:" + str(e))
            # Try again with the same problem
            i -= 1
            continue

        # Get solution by running the code
        solution, actual_solution = 'N/A', 'N/A'
        try:
            # remove wrappers
            if '```python' in cpmpy_answer:
                code = cpmpy_answer.split('```python')[1].split('```')[0]
            else:
                code = cpmpy_answer

            actual_solution = run_code(prob.cpmpy_code)
            print(f'ACTUAL SOLUTION:\n{actual_solution}\n')

            solution = run_code(code)
            print(f'SOLUTION:\n{solution}\n')

            # compare
            if solution.strip() != actual_solution.strip():
                print("Solutions are not equivalent")
                sol_wrong += 1
                sol_log = 'False'
            else:
                sol_log = 'True'
                print("Solutions are equivalent")
        except Exception as e:
            print("Error while running code:" + str(e))
            sol_log = 'Error: ' + str(e)
            sol_err += 1


        # SOLUTION EVALUATION #2, put the predicted model's solution as a constraint in the actual model and check if it is SAT
        predicted_solution = None
        try:

            # remove wrappers
            if '```python' in cpmpy_answer:
                code = cpmpy_answer.split('```python')[1].split('```')[0]
            else:
                code = cpmpy_answer

            predicted_solution = run_code(code)
            print(f'Predicted SOLUTION:\n{predicted_solution}\n')

            if predicted_solution is None:
                sol_2 = cpmpy_model_is_unsat(prob.cpmpy_model)
                if sol_2:
                    print("Solution 2 successful")
                    sol_2_log = 'True'
                else:
                    print("Solution 2 failed")
                    sol_2_wrong += 1
                    sol_2_log = 'False'
            else:
                # predicted solution is a json object
                predicted_solution = json.loads(predicted_solution)
                # get keys
                keys = list(predicted_solution.keys())
                # add each key as a constraint in code

                _consts_to_add = ''
                for key in keys:
                    _consts_to_add += f'm += {key} == {predicted_solution[key]}\n'

                new_code = prob.cpmpy_code + '\n' + _consts_to_add + '\n'
                new_code += 'print(f"Model Solved: {m.solve(time_limit=10)}, Status: {m.status()}")\n'
                code_output = run_code(new_code)
                sol_2 = "Model Solved: True" in code_output
                if sol_2:
                    print("Solution 2 successful")
                    sol_2_log = 'True'
                else:
                    print("Solution 2 failed")
                    sol_2_wrong += 1
                    sol_2_log = 'False'

        except Exception as e:
            print("Error when trying to check solution 2 from predicted model: " + str(e))
            sol_2_log = 'Error when trying to check solution 2 from predicted model: ' + str(e)
            sol_2_err += 1

        if sol_2_log == 'True' or sol_log == 'True':
            print("Final solution is correct")
            sol_final_correct += 1



        # MODEL EVALUATION
        try:
            if check_cpmpy_str_models_equivalence(cpmpy_answer, prob.cpmpy_code, True):
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

        # CONSTRAINT EVALUATION
        try:
            wrong_consts, total_consts = get_cpmpy_str_per_const_eval(cpmpy_answer, prob.cpmpy_code, True)
            const_wrong += wrong_consts
            const_total += total_consts
            const_log = f'Wrong: {wrong_consts}, Total: {total_consts}'
            print(const_log)
        except Exception as e:
            print("Error in constraint evaluation: " + str(e))
            const_log = 'Error in constraint evaluation: ' + str(e)
            n_consts = get_number_of_constraints(prob.cpmpy_code)
            const_err += n_consts
            const_total += n_consts

        # log
        to_log.append({
            'question': question,
            'pseudo_model': pseudo_model_answer,
            'cpmpy_model': cpmpy_answer,
            'solution': solution,
            'actual_solution': actual_solution,
            'solution_log': sol_log,
            'solution_2_log': sol_2_log,
            'model_log': mod_log,
            'constraint_log': const_log
        })

    total = len(DATASET)
    sol_acc = 100 * (total - sol_wrong - sol_err) / total
    sol_2_acc = 100 * (total - sol_2_wrong - sol_2_err) / total
    final_sol_acc = 100 * sol_final_correct / total
    mod_acc = 100 * (total - prob_wrong - prob_err) / total
    const_acc = 100 * (const_total - const_wrong - const_err) / const_total

    print(f"Total problems: {total}")
    print(f"Model accuracy: {mod_acc:.2f}%")
    print(f"Solution accuracy: {sol_acc:.2f}%")
    print(f"Solution 2 accuracy: {sol_2_acc:.2f}%")
    print(f"Final solution accuracy: {final_sol_acc:.2f}%")
    print(f"Constraint accuracy: {const_acc:.2f}%")
    print()
    print(f"Problems with wrong models: {prob_wrong}")
    print(f"Problems with errors in model evaluation: {prob_err}")
    print(f"Problems with wrong solutions: {sol_wrong}")
    print(f"Problems with errors in solution evaluation: {sol_err}")
    print(f"Problems with wrong solution 2: {sol_2_wrong}")
    print(f"Problems with errors in solution 2 evaluation: {sol_2_err}")
    print(f"Problems with correct final solution: {sol_final_correct}")
    print(f"Constraints with wrong models: {const_wrong}")
    print(f"Constraints with errors in model evaluation: {const_err}")
    print(f"Total constraints: {const_total}")

    # log to file
    pref = 'pseudo_model' if with_pseudo else 'cpmpy_model'
    pref = 'ner' if with_ner else pref

    if EXAMPLES_SELECTOR == 'mmr' or EXAMPLES_SELECTOR == 'sim':
        examples_pref = 'reversed_' if REVERSED_ORDER_ICL else 'normal_'
        examples_pref += EXAMPLES_SELECTOR
    else:
        examples_pref = EXAMPLES_SELECTOR

    path_to_results = f'results/APLAI/{pref}/{NUM_EXAMPLES}-shot/{examples_pref}/{MODEL}'
    if not os.path.exists(path_to_results):
        os.makedirs(path_to_results)
    with open(f'{path_to_results}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Solution accuracy: {sol_acc}%\n")
        f.write(f"Solution 2 accuracy: {sol_2_acc}%\n")
        f.write(f"Final solution accuracy: {final_sol_acc}%\n")
        f.write(f'Constraint accuracy: {const_acc}%\n')
        f.write(f'Model accuracy: {mod_acc}%\n\n')
        f.write(f'Wrong solutions: {sol_wrong}, total: {total}\n')
        f.write(f'Wrong solution 2: {sol_2_wrong}, total: {total}\n')
        f.write(f'Correct final solutions: {sol_final_correct}, total: {total}\n')
        f.write(f'Wrong constraints: {const_wrong}, total: {const_total}\n')
        f.write(f'Wrong models: {prob_wrong}, total: {total}\n')
        f.write(f'Errors: solution-level: {sol_err}, constraint-level: {const_err}, model-level: {prob_err}\n')
        f.write('---------------------------------------------------------------------------------------------\n\n')
        for item in to_log:
            f.write(f"Question: {item['question']}\n")
            f.write(f"PREDICTED Pseudo model: {item['pseudo_model']}\n")
            f.write(f"PREDICTED CPMPy model: {item['cpmpy_model']}\n")
            f.write(f"Solution from predicted model: {item['solution']}\n")
            f.write(f"Actual solution: {item['actual_solution']}\n")
            f.write(f"Solution log: {item['solution_log']}\n")
            f.write(f"Solution 2 log: {item['solution_2_log']}\n")
            f.write(f"Model log: {item['model_log']}\n")
            f.write(f"Constraint log: {item['constraint_log']}\n")
            f.write('---------------------------------------------------------------------------------------------\n\n')


def run_aplai_pipeline(method):
    if method == 'DIRECT':
        print('Running direct solution pipeline on APLAI problems')
        pipeline_direct_solution()
    elif method == 'CPMPY':
        print('Running CPMPy model pipeline on APLAI problems')
        pipeline_cpmpy_model()  # CPMpy
    elif method == 'PSEUDO':
        print('Running Pseudo model pipeline on APLAI problems')
        pipeline_cpmpy_model(with_pseudo=True)  # Pseudo and Cpmpy
    elif method == 'NER':
        print('Running NER model pipeline on APLAI problems')
        pipeline_cpmpy_model(with_pseudo=True, with_ner=True)  # NER and Pseudo and Cpmpy
    else:
        raise ValueError(f"Not supported method: {method}")
