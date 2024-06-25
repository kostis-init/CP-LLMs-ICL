import os
from json import load

import numpy as np
from jsonlines import jsonlines

from llms4cp.dataset_classes import Puzzle, CanonicalFormulation, APLAIProblem


def get_puzzle_dirs(with_train=False, only_train=False, only_logicia_test=False) -> [str]:
    extra_test = [f'data/LGPs/test/puzzle_{i}/' for i in range(1, 51)]
    extra_test_na = [f'data/LGPs/test_na/puzzle_{i}/' for i in range(1, 51)]
    extra_train = [f'data/LGPs/train/puzzle_{i}/' for i in range(1, 51)]

    puzzle_dirs = extra_test + extra_test_na

    if only_train:
        return extra_train
    if only_logicia_test:
        return extra_test + extra_test_na
    if with_train:
        puzzle_dirs += extra_train

    return puzzle_dirs


def get_puzzles(with_train=False, only_train=False, only_logicia_test=False) -> [Puzzle]:
    puzzle_dirs = get_puzzle_dirs(with_train=with_train, only_train=only_train, only_logicia_test=only_logicia_test)

    puzzles = []

    for puzzle_dir in puzzle_dirs:
        if not os.path.exists(puzzle_dir):
            continue

        with open(puzzle_dir + 'entities.txt', 'r') as f:
            entities = f.read().splitlines()
        with open(puzzle_dir + 'clues.txt', 'r') as f:
            clues = f.read().splitlines()
        with open(puzzle_dir + 'answerActual.txt', 'r') as f:
            answer_actual = f.read().splitlines()
        with open(puzzle_dir + 'label.json', 'r') as f:
            label = load(f)

        if os.path.exists(puzzle_dir + 'cpmpy_model.txt'):
            with open(puzzle_dir + 'cpmpy_model.txt', 'r') as f:
                cpmpy_model = f.read()
        else:
            cpmpy_model = None

        if os.path.exists(puzzle_dir + 'cpmpy_model.py'):
            with open(puzzle_dir + 'cpmpy_model.py', 'r') as f:
                cpmpy_model = '```python\n' + f.read() + '\n```'

        if os.path.exists(puzzle_dir + 'direct_solution.txt'):
            with open(puzzle_dir + 'direct_solution.txt', 'r') as f:
                direct_solution = f.read()
        else:
            direct_solution = ''

        if os.path.exists(puzzle_dir + 'pseudo_model.txt'):
            with open(puzzle_dir + 'pseudo_model.txt', 'r') as f:
                pseudo_model = f.read()
        else:
            pseudo_model = ''

        if os.path.exists(puzzle_dir + 'ner.txt'):
            with open(puzzle_dir + 'ner.txt', 'r') as f:
                ner = eval(f.read())
        else:
            ner = []

        entities = dict(zip(entities[0].split(', '), [x.split(', ') for x in entities[2:] if x.strip() != '']))
        answer_actual = [x.split(', ') for x in answer_actual]

        puzzles.append(
            Puzzle(entities, clues, answer_actual, label, puzzle_dir, cpmpy_model, direct_solution, pseudo_model, ner))

    return puzzles


def read_nl4opt_test_data():
    path_to_dataset = 'data/nl4opt/test_new_with_rag.jsonl'
    dataset = []
    with jsonlines.open(path_to_dataset) as reader:
        for i, line in enumerate(reader.iter()):
            for key, value in line.items():
                data = value
            order_mapping = data['order_mapping']  # {"sled dogs": 0, "trucks": 1, "truck": 1, "sled dog": 0}
            document = data['document']  # problem description (str)
            canonical = CanonicalFormulation(np.array(data['canonical']['objective']),
                                             np.array(data['canonical']['constraints']))
            entities = data['entities'] if 'entities' in data else None
            cpmpy_code = data['cpmpy_code'] if 'cpmpy_code' in data else None
            dataset.append((document, order_mapping, canonical, entities, cpmpy_code))
    return dataset


def read_aplai_data():
    aplai_problems_directories_prefix = 'data/APLAI_course/'
    aplai_problems_directories = [
        aplai_problems_directories_prefix + 'ex1s1/',
        aplai_problems_directories_prefix + 'ex1s2/',
        aplai_problems_directories_prefix + 'ex1s3/',
        aplai_problems_directories_prefix + 'ex1s4/',
        aplai_problems_directories_prefix + 'ex1s5/',
        aplai_problems_directories_prefix + 'ex1s6/',

        aplai_problems_directories_prefix + 'ex2s1/',
        aplai_problems_directories_prefix + 'ex2s2/',
        aplai_problems_directories_prefix + 'ex2s3/',
        aplai_problems_directories_prefix + 'ex2s4/',
        aplai_problems_directories_prefix + 'ex2s5/',

        aplai_problems_directories_prefix + 'ex3s1/',
        aplai_problems_directories_prefix + 'ex3s2/',
        aplai_problems_directories_prefix + 'ex3s3/',
        aplai_problems_directories_prefix + 'ex3s4/',

        aplai_problems_directories_prefix + 'ex5s1/',
        aplai_problems_directories_prefix + 'ex5s2/',
        aplai_problems_directories_prefix + 'ex5s3/',
        # aplai_problems_directories_prefix + 'ex5s4/',
    ]

    problems = []

    # read the description.txt from each directory
    for prob_dir in aplai_problems_directories:
        with open(prob_dir + 'description.txt', 'r') as f:
            description = f.read()

        if os.path.exists(prob_dir + 'cpmpy_model.py'):
            with open(prob_dir + 'cpmpy_model.py', 'r') as f:
                cpmpy_code = f.read()
        else:
            cpmpy_code = None

        if os.path.exists(prob_dir + 'data.json'):
            with open(prob_dir + 'data.json', 'r') as f:
                data_json = load(f)
        else:
            data_json = None

        if os.path.exists(prob_dir + 'direct_solution.txt'):
            with open(prob_dir + 'direct_solution.txt', 'r') as f:
                direct_solution = f.read()
        else:
            direct_solution = ''

        if os.path.exists(prob_dir + 'blueprint.txt'):
            with open(prob_dir + 'blueprint.txt', 'r') as f:
                pseudo_model = f.read()
        else:
            pseudo_model = ''

        problems.append(APLAIProblem(description, cpmpy_code, data_json, direct_solution, pseudo_model))

    return problems
