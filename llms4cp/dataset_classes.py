from typing import Dict
from dataclasses import dataclass
import numpy as np


class APLAIProblem:
    def __init__(self, description, cpmpy_code, data_json, direct_solution, pseudo_model):

        # remove everything before the line that contains from cpmpy (excluding that line)
        cpmpy_code = cpmpy_code.split("\n")
        for i, line in enumerate(cpmpy_code):
            if "from cpmpy" in line:
                cpmpy_code = cpmpy_code[i:]
                break
        cpmpy_code = "\n".join(cpmpy_code)

        self.description = description
        self.question = description
        self.cpmpy_code = cpmpy_code
        self.cpmpy_code_wrapped = f'```python\n{cpmpy_code}\n```'
        self.data_json = data_json
        self.data_str = str(data_json)
        self.direct_solution = direct_solution
        self.pseudo_model = pseudo_model
        self.entities_as_str = ''



class Nl4optProblem:
    def __init__(self, document, order_mapping, cpmpy_code, solution, canonical, pseudo_model, direct_solution,
                 entities):
        self.document = document
        self.question = document
        self.order_mapping = order_mapping
        self.cpmpy_code = cpmpy_code
        self.cpmpy_code_wrapped = f'```python\n{cpmpy_code}\n```'
        self.solution = solution
        self.canonical = canonical
        self.pseudo_model = pseudo_model
        self.direct_solution = direct_solution
        self.entities = entities
        self.entities_as_str = ''
        for entity in entities:
            self.entities_as_str += entity['entity_group'] + ' (' + str(entity['start']) + '-' + str(
                entity['end']) + '): ' + entity['word'] + '\n'


class Puzzle:
    def __init__(self, entities: Dict[str, str], clues: [str], answer_actual: [[str]],
                 label: Dict[str, str], file_name: str, cpmpy_model: str, direct_solution: str, pseudo_model: str,
                 ner: []):
        self.entities = entities
        self.clues = clues
        self.answer_actual = answer_actual
        self.label = label
        self.file_name = file_name
        self.cpmpy_model = cpmpy_model
        self.cpmpy_code_wrapped = cpmpy_model
        if '```python' not in cpmpy_model:
            self.cpmpy_code_wrapped = f'```python\n{cpmpy_model}\n```'
        self.direct_solution = direct_solution
        self.pseudo_model = pseudo_model
        self.ner = ner
        self.entities_as_str = ''
        self.question = self.format_question()
        for entity in ner:
            self.entities_as_str += entity['entity_group'] + ' (' + str(entity['start']) + '-' + str(
                entity['end']) + '): ' + entity['word'] + '\n'

    def format_question(self) -> str:
        return "Clues:\n" + "\n".join(self.clues) + "\n\nEntities:\n" + "\n".join(
            [f"{k}: {', '.join(v)}" for k, v in self.entities.items()])


@dataclass
class CanonicalFormulation:
    objective: np.ndarray
    constraints: np.ndarray


class CpmpyModelWithVars:
    def __init__(self, model, vars_):
        self.model = model
        self.vars_ = vars_
