import json

from jsonlines import jsonlines
import cpmpy
import numpy as np

from llms4cp.dataset_classes import CanonicalFormulation

MAX_INT = 100_000_000

var_to_idx = {"x": 0, "y": 1, "z": 2, "w": 3}


def solve_lp(canonical: CanonicalFormulation):
    # Variables
    num_vars = len(canonical.objective)
    var_labels = list(var_to_idx.keys())[:num_vars]
    vars_ = [cpmpy.intvar(0, MAX_INT, name=var_label) for var_label in var_labels]

    # Constraints
    model_ = cpmpy.Model()
    for constraint in canonical.constraints:
        # constraint is an array of num_vars + 1 elements, where the last element is the rhs
        # and the rest are the coefficients of the variables
        # e.g. [1, 2, 3, 4, 5] means 1x + 2y + 3z + 4w <= 5
        coeffs = constraint[:-1]
        rhs = constraint[-1]

        # if coeffs and rhs are not integers, multiply by 1000
        if not all(isinstance(x, int) for x in coeffs):
            coeffs = [int(x * 1000) for x in coeffs]
            rhs = int(rhs * 1000)

        # add constraint to model
        model_ += sum([coeff * var for coeff, var in zip(coeffs, vars_)]) <= rhs

    # Objective (minimize)
    coeffs = canonical.objective
    # if coeeffs are not integers, multiply by 1000
    if not all(isinstance(x, int) for x in coeffs):
        coeffs = [int(x * 1000) for x in coeffs]
    model_.minimize(sum([coeff * var for coeff, var in zip(coeffs, vars_)]))

    # Prepare for solution
    var_labels_values = dict()
    for var_label, var in zip(var_labels, vars_):
        var_labels_values[var_label] = var

    solved = model_.solve(time_limit=10)

    if not solved:
        print("NOT SOLVED")
        return None

    solution = dict()
    for var_label, cpmpy_var in var_labels_values.items():
        solution[var_label] = cpmpy_var.value()
    return solution


new_file = open('../../data/nl4opt/train_new.jsonl', 'w')

with jsonlines.open('../../data/nl4opt/train_reduced_with_explanations_detailed_with_canonical.jsonl') as reader:
    for i, line in enumerate(reader.iter()):
        doc_id, doc_obj = list(line.items())[0]
        document = doc_obj['document']
        order_mapping = doc_obj['order_mapping']
        obj_declaration = doc_obj['obj_declaration']
        const_declarations = doc_obj['const_declarations']
        explanation = line['explanation']
        canonical = line['canonical']

        # TypeError: Object of type ndarray is not JSON serializable, so convert to list
        canonical_obj = CanonicalFormulation(
            np.array(canonical['objective']),
            np.array(canonical['constraints'])
        )

        solution = solve_lp(canonical_obj)

        line = {
            "doc_id": doc_id,
            "document": document,
            "order_mapping": order_mapping,
            "obj_declaration": obj_declaration,
            "const_declarations": const_declarations,
            "explanation": explanation,
            "canonical": canonical,
            "solution": solution
        }

        new_file.write(json.dumps(line))
        new_file.write('\n')
