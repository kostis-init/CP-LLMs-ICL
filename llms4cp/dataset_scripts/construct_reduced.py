import json

from jsonlines import jsonlines


def construct_reduced_train():
    # create new file ../data/train_reduced.jsonl
    new_file = open('../../data/nl4opt/train_reduced.jsonl', 'w')

    with jsonlines.open('../../data/nl4opt/train.jsonl') as reader:
        for line in reader.iter():
            for key, value in line.items():
                data = value
            order_mapping = data['order_mapping']
            document = data['document']
            obj_declaration = data['obj_declaration']
            const_declarations = data['const_declarations']

            new_file.write(json.dumps({key:
                                           {"document": document, "order_mapping": order_mapping,
                                            "obj_declaration": obj_declaration,
                                            "const_declarations": const_declarations}}))
            new_file.write('\n')


def construct_reduced_test():
    # create new file ../data/train_reduced.jsonl
    new_file = open('../../data/nl4opt/corrected_test_reduced.jsonl', 'w')

    with jsonlines.open('../../data/nl4opt/corrected_test.jsonl') as reader:
        for line in reader.iter():
            for key, value in line.items():
                data = value
            order_mapping = data['order_mapping']
            document = data['document']
            obj_declaration = data['obj_declaration']
            const_declarations = data['const_declarations']

            new_file.write(json.dumps(
                {key: {"document": document, "order_mapping": order_mapping, "obj_declaration": obj_declaration,
                       "const_declarations": const_declarations}}))
            new_file.write('\n')


if __name__ == "__main__":
    # construct_reduced_train()
    # construct_reduced_test()

    pass
