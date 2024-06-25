import anthropic
import together
import os
from openai import OpenAI

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
TOGETHER_API_KEY = 'YOUR_TOGETHER_API_KEY'
DEEPSEEK_API_KEY = 'YOUR_DEEPSEEK_API_KEY'
ANTHROPIC_API_KEY = 'YOUR_ANTHROPIC_API_KEY'

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY
together.api_key = TOGETHER_API_KEY

# ANTHROPIC
# MODEL = 'claude-3-sonnet-20240229'
# MODEL = 'claude-3-haiku-20240307'

# OPEN AI
# MODEL = "gpt-4-0125-preview"
MODEL = "gpt-3.5-turbo-0125"

# CODE MODELS
# MODEL = 'deepseek-coder'
# MODEL = 'WizardLM/WizardCoder-Python-34B-V1.0'
# MODEL = 'WizardLM/WizardCoder-15B-V1.0'
# MODEL = 'Phind/Phind-CodeLlama-34B-v2'

# VARIOUS
# MODEL = 'google/gemma-7b-it'
# MODEL = 'deepseek-chat'
# MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
# MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
# MODEL = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
# MODEL = "NousResearch/Nous-Hermes-2-Yi-34B"
# MODEL = "mistralai/Mistral-7B-v0.1"
# MODEL = "mistralai/Mixtral-8x7B-v0.1"
# MODEL = "togethercomputer/Llama-2-7B-32K-Instruct"
# MODEL = "zero-one-ai/Yi-34B-Chat"
# MODEL = "deepseek-ai/deepseek-coder-33b-instruct"
# MODEL = "codellama/CodeLlama-70b-Python-hf"

# QWEN
# MODEL = 'Qwen/Qwen1.5-0.5B-Chat'
# MODEL = 'Qwen/Qwen1.5-1.8B-Chat'
# MODEL = 'Qwen/Qwen1.5-4B-Chat'
# MODEL = 'Qwen/Qwen1.5-7B-Chat'
# MODEL = 'Qwen/Qwen1.5-14B-Chat'
# MODEL = 'Qwen/Qwen1.5-72B-Chat'

if MODEL.startswith('gpt'):
    LLM_CLIENT = OpenAI()
elif 'claude' in MODEL:
    LLM_CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
elif MODEL == 'deepseek-coder' or MODEL == 'deepseek-chat':
    LLM_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
else:
    LLM_CLIENT = OpenAI(api_key=TOGETHER_API_KEY, base_url="https://api.together.xyz/v1")

LIMIT = 999

NUM_EXAMPLES = 4

# EXAMPLES_SELECTOR = "static"
# EXAMPLES_SELECTOR = "rand"
# EXAMPLES_SELECTOR = "lsrd"
# EXAMPLES_SELECTOR = "sim"
EXAMPLES_SELECTOR = "mmr"

REVERSED_ORDER_ICL = True
# REVERSED_ORDER_ICL = False


"""
System messages
"""

# NL4OPT

SYSTEM_MESSAGE_NL4OPT_SOLVE = """\
Solve the given problem. You can give any rationale you want, but always end with the final answer in a structured way.
You are an expert at solving constrained optimization problems. You always end your responses with the assignment \
of values to the variables like this:
### FINAL ANSWER: {...}

It is mandatory that the last line of your response ends with the json object that contains the final assignment of \
values to the variables and only that, or UNSATISFIABLE if the problem is unsatisfiable.
"""

SYSTEM_MESSAGE_CPMPY_NL4OPT = """\
Your task is to convert optimization problems into their constraint programming CPMpy models in python code. Instructions:
- The variable names should be descriptive.
- The constraints must represent the problem correctly.
- Never try to solve the given problem, neither manually nor programmatically.
- The generated code should be syntactically and semantically correct.
"""

SYSTEM_MESSAGE_PSEUDO_NL4OPT = """\
Your task is to transform problems described in plain English to a structured constraint programming pseudo-model that \
contains at least: Variables, Constraints, and Objective. You should never try to solve the given problem, even if the \
given problem is trivial. Your task is to describe it as a constraint programming pseudo-model.
"""

# LGPS

SYSTEM_MESSAGE_LGP_SOLVE = """
Your task is to solve the given logic grid puzzles.
Your answers must end with the same format in the answer, which is:
### FINAL ANSWER: {"mappings": [{}, {}, ...]}

The mappings are the final assignment of values to the variables.
This should be a json object with key "mappings" and value a list of objects where in each one a mapping between entities is represented.
"""

SYSTEM_MESSAGE_PSEUDO_LGPS = """\
Your task is to transform logic grid puzzle problems described in plain English to a structured constraint programming pseudo-model. You should never try to solve the given problem, even if the \
given problem is trivial. Your task is to describe it as a constraint programming pseudo-model. All your responses should follow the same pattern.
"""

SYSTEM_MESSAGE_CPMPY_LGPS = """\
Your task is to convert logic grid puzzle problems into their constraint programming CPMpy models in python code. Instructions:
- The generated code must be semantically and syntactically correct (use new lines to easily open and close parentheses).
- Never try to solve the given problem, neither manually nor programmatically, just model it.
- You can only use the following global and builtin constraints: AllDifferent, Xor, implies, & (logical and), ==, !=, >, >=, <, <=.
    - AllDifferent([x, y, z, ...]) expresses that x, y, z, ... are all different.
    - Xor([x, y, z, ...]) expresses that either x, or y, or z, ... is true, but not more than one.
    - x.implies(y) expresses that if x is true, then y must be true.
    - The rest of the constraints are self-explanatory.
"""

# APLAI

SYSTEM_MESSAGE_APLAI_SOLVE = """\
Your task is to solve the given problem. You can give any rationale you want, but always end with the final answer in a structured way.
You are an expert at solving constraint problems. You always end your responses with the assignment \
of values to the variables like this:
### FINAL ANSWER: {...}

It is mandatory that the last line of your response ends with the json object that contains the final assignment of \
values to the variables and only that (all in one line: the last line), or UNSATISFIABLE if the problem is unsatisfiable.
"""

SYSTEM_MESSAGE_PSEUDO_APLAI = """\
Your task is to transform problems described in plain English to a structured constraint programming pseudo-model that \
contains at least: Variables, Constraints, and Objective. You should never try to solve the given problem, even if the \
given problem is trivial. Your task is to describe it as a constraint programming pseudo-model.
"""

SYSTEM_MESSAGE_CPMPY_APLAI = """\
Your task is to convert combinatorial or mathematical or logical problems into their constraint programming CPMpy models in python code.
Instructions:
- Never try to solve the given problem manually, only provide the CPMpy model to print the solution in the format specified in the problem description.
- Remember that CPMpy is a Constraint Programming and Modeling library in Python, based on numpy.
- The generated code should be syntactically and semantically correct.
"""