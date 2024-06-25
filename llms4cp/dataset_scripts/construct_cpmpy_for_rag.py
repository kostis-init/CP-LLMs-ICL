import json

from jsonlines import jsonlines

from openai import OpenAI

from llms4cp.in_context_config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4-0125-preview"


def call_gpt(selected_examples, user_prompt):
    messages = [{"role": "system",
                 "content": "You will be given constrained optimization problems along with their modelling. Your task is to produce the python code that models theses problems using the CPMpy library."}]

    for example in selected_examples:
        for k, v in example.items():
            role = "assistant" if k == "output" else "user"
            messages.append({"role": role, "content": v})

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        messages=messages,
        model=MODEL, temperature=0, max_tokens=2000, top_p=0, frequency_penalty=0, presence_penalty=0)

    # print(response)
    return response.choices[0].message.content


new_file = open('../../data/nl4opt/test_new_with_rag.jsonl', 'w')

with jsonlines.open('../../data/nl4opt/train_new_with_rag.jsonl') as reader:
    selected_examples = []

    for i, line in enumerate(reader.iter()):
        if i > 5:
            break
        in_ = f'Problem: {line["document"]}\nOrder Mapping: {line["order_mapping"]}\nObjective: {line["obj_declaration"]}\nConstraints: {line["const_declarations"]}\n'

        out_ = f'```python\n{line["cpmpy_code"]}\n```'

        selected_examples.append({"input": in_, "output": out_})

    print(selected_examples)

with jsonlines.open('../../data/nl4opt/test_new.jsonl') as reader:
    for i, line in enumerate(reader.iter()):
        print(i)

        doc_id, doc_obj = list(line.items())[0]
        document = doc_obj['document']

        in_ = f'Problem: {doc_obj["document"]}\nOrder Mapping: {doc_obj["order_mapping"]}\nObjective: {doc_obj["obj_declaration"]}\nConstraints: {doc_obj["const_declarations"]}\n'

        answer = call_gpt(selected_examples, in_)

        if '```python' in answer:
            cpmpy_code = answer.split('```python')[1].split('```')[0]
        else:
            cpmpy_code = ''

        print('ANSWER\n' + answer)
        print('CPMPY\n' + cpmpy_code)

        line[doc_id]['cpmpy_code'] = cpmpy_code
        new_file.write(json.dumps(line))
        new_file.write('\n')
