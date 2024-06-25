import time
from typing import Dict
from llms4cp.in_context_config import *


def get_contents(example, method, step):
    if method == 'CPMPY':
        content_user = example["question"]
        content_assistant = example["cpmpy_code"]
    elif method == 'PSEUDO':
        if step == 'GEN_PSEUDO':
            content_user = example["question"]
            content_assistant = example["pseudo_model"]
        elif step == 'GEN_CPMPY':
            content_user = example["question"] + '\n' + example["pseudo_model"]
            content_assistant = example["cpmpy_code"]
        else:
            raise ValueError(f"Step {step} not supported")
    elif method == 'NER':
        if step == 'GEN_PSEUDO':
            content_user = example["question"] + '\n' + example["ner"]
            content_assistant = example["pseudo_model"]
        elif step == 'GEN_CPMPY':
            content_user = example["question"] + '\n' + example["ner"] + '\n' + example["pseudo_model"]
            content_assistant = example["cpmpy_code"]
        else:
            raise ValueError(f"Step {step} not supported")
    elif method == 'DIRECT':
        content_user = example["question"]
        content_assistant = example["direct_solution"]
    else:
        raise ValueError(f"Method {method} not supported")
    return content_assistant, content_user


def call_gpt(selected_examples: [Dict[str, str]], user_prompt: str, system_message, model, client, method, step):
    messages = [{"role": "system", "content": system_message}]

    for example in selected_examples:
        content_assistant, content_user = get_contents(example, method, step)
        messages.append({"role": "user", "content": content_user})
        messages.append({"role": "assistant", "content": content_assistant})

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0.0,
        max_tokens=2000,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
    )

    print(response)
    return messages, response.choices[0].message.content


def call_anthropic(selected_examples, user_prompt, system_message, model, client, method, step):
    messages = []
    for example in selected_examples:
        content_assistant, content_user = get_contents(example, method, step)
        messages.append({"role": "user", "content": content_user})
        messages.append({"role": "assistant", "content": content_assistant})
    messages.append({"role": "user", "content": user_prompt})

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        temperature=0.0,
        system=system_message,
        messages=messages
    )

    print(response)
    return messages, response.content[0].text


def call_llm(selected_examples: [Dict[str, str]], user_prompt: str, system_message, model=MODEL, client=LLM_CLIENT,
             method='CPMPY', step='GEN_CPMPY'):
    if MODEL.startswith("gpt"):
        messages, answer = call_gpt(selected_examples, user_prompt, system_message, model, client, method, step)
    elif 'claude' in MODEL:
        messages, answer = call_anthropic(selected_examples, user_prompt, system_message, model, client, method, step)
        # wait 2 seconds
        time.sleep(2)
    else:
        # count time
        start = time.time()
        messages, answer = call_gpt(selected_examples, user_prompt, system_message, model, client, method, step)
        end = time.time()
        # if less than 1 second, wait until 1 second has passed
        if end - start < 1.2:
            time.sleep(1.1 - (end - start))
    return messages, answer
