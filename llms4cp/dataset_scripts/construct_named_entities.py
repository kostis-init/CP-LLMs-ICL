import json

from jsonlines import jsonlines
from ner4opt import Ner4Opt

ner4opt = Ner4Opt(model="hybrid")

new_file = open('../../data/nl4opt/train_new_with_rag_and_ner.jsonl', 'w')

with jsonlines.open('../../data/nl4opt/train_new_with_rag.jsonl') as reader:
    for i, line in enumerate(reader.iter()):
        print(i)
        document = line['document']
        try:
            entities = ner4opt.get_entities(document)
        except Exception as e:
            print('Error:', e)
            entities = []
        line['entities'] = entities
        new_file.write(json.dumps(line))
        new_file.write('\n')
