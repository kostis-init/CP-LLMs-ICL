from jsonlines import jsonlines

from llms4cp.dataset_classes import CanonicalFormulation
from llms4cp.lgps_cpmpy_model_equivalence import check_cpmpy_with_cpmpy_str_model_equivalence
from llms4cp.nl4opt_pipeline import get_cpmpy_model_from_canonical

with jsonlines.open('../../data/nl4opt/train_new_with_rag_and_ner.jsonl') as reader:
    for i, line in enumerate(reader.iter()):
        cpmpy_code_str = line["cpmpy_code"]
        order_mapping = line["order_mapping"]
        solution = line["solution"]
        canonical_obj = line["canonical"]['objective']
        canonical_const = line["canonical"]['constraints']

        cpmpy_canonical = get_cpmpy_model_from_canonical(CanonicalFormulation(canonical_obj, canonical_const))
        check = check_cpmpy_with_cpmpy_str_model_equivalence(cpmpy_code_str, cpmpy_canonical)
        if not check:
            print(
                f'i = {i}, document : {line["document"]}\n cpmpy_code_str = {cpmpy_code_str}\n cpmpy_canonical = {cpmpy_canonical.model}')

# with jsonlines.open('../data/nl4opt/test_new_with_rag.jsonl') as reader:
#     for i, line in enumerate(reader.iter()):
#
#
#         doc_id, doc_obj = list(line.items())[0]
#         document = doc_obj['document']
#
#         cpmpy_code_str = doc_obj["cpmpy_code"]
#         solution_str = doc_obj["solution"]
#         canonical = doc_obj["canonical"]
#         # print(cpmpy_code_str)
#         # print(solution_str)
#         # print(canonical)
#         canonical_obj = canonical['objective']
#         canonical_const = canonical['constraints']
#
#         cpmpy_canonical = get_cpmpy_model_from_canonical(CanonicalFormulation(canonical_obj, canonical_const))
#         check = check_cpmpy_with_cpmpy_str_model_equivalence(cpmpy_code_str, cpmpy_canonical)
#         if not check:
#             print(f'i = {i}, document : {document}\n cpmpy_code_str = {cpmpy_code_str}\n cpmpy_canonical = {cpmpy_canonical.model}')
