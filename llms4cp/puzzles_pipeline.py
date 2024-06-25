from datetime import datetime
from llms4cp.call_llms import call_llm
from llms4cp.data_reader import get_puzzles
from llms4cp.dataset_classes import Puzzle
from llms4cp.lgps_cpmpy_model_equivalence import check_cpmpy_str_models_equivalence, get_cpmpy_str_per_const_eval
from llms4cp.util import run_code, format_final_executable, choose_example_selector, execute_and_get_solution, \
    cpmpy_model_is_unsat, get_examples_for_context, get_number_of_constraints, get_var_names_from_exec_model_str
from llms4cp.in_context_config import *
import numpy as np

# set random seed
np.random.seed(42)

# Setup the train dataset
LGPS_TRAIN: [Puzzle] = get_puzzles(only_train=True)
if EXAMPLES_SELECTOR == "rand" or EXAMPLES_SELECTOR == "lsrd":
    np.random.seed(42)
    np.random.shuffle(LGPS_TRAIN)


def pipeline_direct_solution():
    """ Here we check with LLMs providing the solution directly"""
    puzzles = get_puzzles(only_logicia_test=True)
    wrong, total = 0, 0
    errors = 0
    to_log = []

    for i, puzzle in enumerate(puzzles):

        if i >= LIMIT:
            break

        try:
            question = puzzle.format_question()

            messages, answer = call_llm(get_examples_for_context(None, None, LGPS_TRAIN), question,
                                        system_message=SYSTEM_MESSAGE_LGP_SOLVE, method='DIRECT')

            lines = answer.splitlines()

            # ### FINAL ANSWER: {"mappings": [{"Cornick", "January", "Techtrin"}, {"Dreadco", "February", "Ubersplore"}, {"Worul", "March", "Permias"}, {"Foltron", "April", "Rubicorp"}]}
            # find the line that contains ### FINAL ANSWER
            answer_line = None
            for i, line in enumerate(lines):
                if "final answer" in line.lower():
                    answer_line = line

            if answer_line is None:
                print("No final answer found")
                errors += 1
                to_log.append((question, answer, 'No final answer found'))
                continue

            # find the json object
            pred_answer_line = answer_line.split("### FINAL ANSWER: ")[1]
            # read it as a dict
            pred_answer_dict = eval(pred_answer_line)
            mappings = pred_answer_dict['mappings']

            # put pred_sol in ground-truth cpmpy model and check if it is satisfied
            code_to_run = format_final_executable(puzzle.cpmpy_model, mappings)
            print(code_to_run)
            output = run_code(code_to_run)
            print(output)

            if "Model Solved: True" in output:
                print("Correct!")
                to_log.append((question, answer, 'Correct'))
            else:
                wrong += 1
                print("Wrong!")
                to_log.append((question, answer, 'Wrong'))
            total += 1

        except Exception as e:
            print("Error")
            print(e)
            errors += 1
            continue

    res_dir = f'results/lgp/direct/{NUM_EXAMPLES}-shot/{EXAMPLES_SELECTOR}/{MODEL}'
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    with open(f'{res_dir}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Wrong: {wrong}, Total: {total}\n")
        f.write(f"Accuracy: {100.0 - (wrong * 100.0 / total)}%\n")
        f.write(f"Errors: {errors}\n")
        f.write('---------------------------------------------------------------------------------------------\n\n')
        for item in to_log:
            for entry in item:
                f.write(f'{entry}\n')
            f.write('---------------------------------------------------------------------------------------------\n\n')


def pipeline_cpmpy_model(with_pseudo=False, with_ner=False):

    dataset = get_puzzles(only_logicia_test=True)
    # dataset = get_puzzles(only_train=True)

    const_wrong, const_total, const_err = 0, 0, 0
    prob_wrong, prob_err = 0, 0
    sol_wrong, sol_err = 0, 0
    sol_inv_wrong, sol_inv_err = 0, 0

    to_log = []

    method = 'CPMPY'
    if with_ner:
        method = 'NER'
    elif with_pseudo:
        method = 'PSEUDO'

    example_selector = choose_example_selector(LGPS_TRAIN)

    for i, prob in enumerate(dataset):
        print(f"Problem {i + 1} / {len(dataset)}")

        # if i < 7:
        #     continue

        if i >= LIMIT:
            break

        question = prob.format_question()
        pseudo_model_answer = 'N/A'
        input_vars = {"question": question}
        if with_ner:
            input_vars["ner"] = prob.entities_as_str
            question += '\n' + prob.entities_as_str

        try:
            if with_pseudo:
                messages, pseudo_model_answer = call_llm(
                    get_examples_for_context(example_selector, input_vars, LGPS_TRAIN),
                    question, system_message=SYSTEM_MESSAGE_PSEUDO_LGPS, method=method, step='GEN_PSEUDO')
                print(f'ANSWER (PSEUDO MODEL):\n{pseudo_model_answer}')
                input_vars["pseudo_model"] = pseudo_model_answer
                question += '\n' + pseudo_model_answer

            messages, cpmpy_answer = call_llm(
                get_examples_for_context(example_selector, input_vars, LGPS_TRAIN),
                question, system_message=SYSTEM_MESSAGE_CPMPY_LGPS, method=method, step='GEN_CPMPY')

            print(f'CPMPY ANSWER:\n{cpmpy_answer}\n')

            # try to run code, if it fails, then we ask again
            # code_to_run = cpmpy_answer.split("```python")[1].split("```")[0]
            # out_ = run_code(code_to_run)
            # print(out_)
            # if out_.strip():
            #     print("Invalid syntax, asking again")
            #     prompt = prompt + '\n' + 'Invalid syntax, please try again. Your previous code:\n' + code_to_run + '\n' + 'The output was:\n' + out_
            #     messages, cpmpy_answer = call_llm(
            #         get_examples_for_context(example_selector, input_vars, LGPS_TRAIN),
            #         prompt, system_message=SYSTEM_MESSAGE_CPMPY_LGPS, method=method, step='GEN_CPMPY')
            #     print(f'CPMPY ANSWER:\n{cpmpy_answer}\n')


        except Exception as e:
            print("Error while calling LLM:" + str(e))
            continue

        # Eval

        # SOLUTION EVALUATION 1 (pred solution should satisfy ground truth model)
        predicted_solution = None
        try:
            predicted_solution = execute_and_get_solution(cpmpy_answer)
            print("Predicted solution: ")
            print(predicted_solution)

            if predicted_solution is None:
                sol_c = cpmpy_model_is_unsat(prob.cpmpy_model)
            else:
                code_output = run_code(format_final_executable(prob.cpmpy_model, predicted_solution))
                sol_c = "Model Solved: True" in code_output

            if not sol_c:
                sol_log = 'False'
                sol_wrong += 1
                print("Solution given by predicted model is wrong")
            else:
                sol_log = 'True'
        except Exception as e:
            print("Error when trying to check solution from predicted model: " + str(e))
            sol_log = 'Error when trying to check solution from predicted model: ' + str(e)
            sol_err += 1

        # SOLUTION EVALUATION 2 (pred model should be satisfied with the ground truth solution)
        try:
            output = run_code(format_final_executable(cpmpy_answer, prob.answer_actual))
            sol_inv_c = "Model Solved: True" in output

            if not sol_inv_c:
                sol_inv_log = 'False'
                sol_inv_wrong += 1
                print("GT solution does NOT satisfy predicted model")
            else:
                sol_inv_log = 'True'
        except Exception as e:
            print("Error when GT solution tried to predicted model: " + str(e))
            sol_inv_log = 'Error when GT solution tried to predicted model: ' + str(e)
            sol_inv_err += 1

        # CONSTRAINT EVALUATION
        try:
            wrong_consts, total_consts = get_cpmpy_str_per_const_eval(cpmpy_answer, prob.cpmpy_model)
            const_wrong += wrong_consts
            const_total += total_consts
            const_log = f'Wrong: {wrong_consts}, Total: {total_consts}'
            print(const_log)
        except Exception as e:
            print("Error in constraint evaluation: " + str(e))
            const_log = 'Error in constraint evaluation: ' + str(e)
            n_consts = get_number_of_constraints(prob.cpmpy_model)
            const_err += n_consts
            const_total += n_consts

        # MODEL EVALUATION
        try:
            if check_cpmpy_str_models_equivalence(prob.cpmpy_model, cpmpy_answer):
                print("Models are equivalent")
                mod_log = 'True'
            else:
                print("Models are not equivalent")
                prob_wrong += 1
                mod_log = 'False'
        except Exception as e:
            print("Error in model evaluation: " + str(e))
            mod_log = 'Error in model evaluation: ' + str(e)
            prob_err += 1

        print("-------------------------------------------------------------")
        to_log.append((question, pseudo_model_answer, cpmpy_answer, predicted_solution, sol_log, sol_inv_log, mod_log, const_log))

    total = len(dataset)
    sol_acc = 100.0 - ((sol_wrong + sol_err) * 100.0 / total)
    inv_sol_acc = 100.0 - ((sol_inv_wrong + sol_inv_err) * 100.0 / total)
    const_acc = 100.0 - ((const_wrong + const_err) * 100.0 / const_total)
    mod_acc = 100.0 - ((prob_wrong + prob_err) * 100.0 / total)

    print(f"Solution accuracy: {sol_acc}%")
    print(f'Inverse Solution accuracy: {inv_sol_acc}%')
    print(f'Constraint accuracy: {const_acc}%')
    print(f'Model accuracy: {mod_acc}%')
    print(f'Wrong solutions: {sol_wrong}, total: {total}')
    print(f'Wrong inverse solutions: {sol_inv_wrong}, total: {total}')
    print(f'Wrong constraints: {const_wrong}, total: {const_total}')
    print(f'Wrong models: {prob_wrong}, total: {total}')
    print(f'Errors: solution-level: {sol_err}, inverse solution-level: {sol_inv_err}, constraint-level: {const_err}, model-level: {prob_err}')

    pref = 'pseudo_model' if with_pseudo else 'cpmpy_model'
    pref = 'ner' if with_ner else pref

    if EXAMPLES_SELECTOR == 'mmr' or EXAMPLES_SELECTOR == 'sim':
        examples_pref = 'reversed_' if REVERSED_ORDER_ICL else 'normal_'
        examples_pref += EXAMPLES_SELECTOR
    else:
        examples_pref = EXAMPLES_SELECTOR

    path_to_results = f'results/lgp/{pref}/{NUM_EXAMPLES}-shot/{examples_pref}/{MODEL}'
    if not os.path.exists(path_to_results):
        os.makedirs(path_to_results)
    with open(f'{path_to_results}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', 'w', encoding="utf-8") as f:
        f.write(f"Solution accuracy: {sol_acc}%\n")
        f.write(f'Inverse Solution accuracy: {inv_sol_acc}%\n')
        f.write(f'Constraint accuracy: {const_acc}%\n')
        f.write(f'Model accuracy: {mod_acc}%\n\n')
        f.write(f'Wrong solutions: {sol_wrong}, total: {total}\n')
        f.write(f'Wrong inverse solutions: {sol_inv_wrong}, total: {total}\n')
        f.write(f'Wrong constraints: {const_wrong}, total: {const_total}\n')
        f.write(f'Wrong models: {prob_wrong}, total: {total}\n')
        f.write(f'Errors: solution-level: {sol_err}, inverse solution-level: {sol_inv_err}, constraint-level: {const_err}, model-level: {prob_err}\n')
        f.write('---------------------------------------------------------------------------------------------\n\n')
        for item in to_log:
            for entry in item:
                f.write(f'{entry}\n')
            f.write('---------------------------------------------------------------------------------------------\n\n')


def run_lgp_pipeline(method):
    if method == 'DIRECT':
        print('Running direct solution pipeline on LGPs')
        pipeline_direct_solution()
    elif method == 'CPMPY':
        print('Running CPMPy model pipeline on LGPs')
        pipeline_cpmpy_model(with_pseudo=False)  # CPMpy
    elif method == 'PSEUDO':
        print('Running Pseudo model pipeline on LGPs')
        pipeline_cpmpy_model(with_pseudo=True)  # Pseudo and Cpmpy
    elif method == 'NER':
        print('Running NER model pipeline on LGPs')
        pipeline_cpmpy_model(with_pseudo=True, with_ner=True)  # NER and Pseudo and Cpmpy
    else:
        raise ValueError(f"Not supported method: {method}")
