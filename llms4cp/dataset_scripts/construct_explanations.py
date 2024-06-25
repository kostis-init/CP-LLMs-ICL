import json

from jsonlines import jsonlines

from openai import OpenAI

from llms4cp.in_context_config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4-1106-preview"


def call_gpt(user_prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You will be given constrained optimization problems along with their modelling in JSON and XML format. Your task is to produce the actual chain of thought that produced the final modelling (variables, objective, constraints, formulation). At the end, you must produce the mathematical formulas of the modelling. Do not use parentheses in the mathematical formulations."
            },
            {
                "role": "user",
                "content": "{\"1045884097\": {\"document\": \"A film production company wants to advertise the release of their new movie using ads in three areas: malls, bus stops, and theatres. They have a weekly advertising budget of $30000. The cost of an ad in each area and their audience reach is given. An ad in a mall costs $5000 and reaches 50000 viewers. An ad at a bus stop costs $1000 and reaches 10000 viewers. An ad in a theatre costs $3000 and reaches 20000 viewers. The city limits the number of ads at a bus stop from a single company to 20. In order to maintain balance, at most a third of the total number of ads should be in theatres and a minimum of 20% of ads should be in malls. How many ads should be run in each of the three areas in order to maximize viewership?\", \"order_mapping\": {\"malls\": 0, \"bus stops\": 1, \"theatres\": 2, \"mall\": 0, \"bus stop\": 1, \"theatre\": 2}, \"obj_declaration\": {\"type\": \"objective\", \"direction\": \"maximize\", \"name\": \"viewership\", \"terms\": {\"mall\": \"50000\", \"bus stop\": \"10000\", \"theatre\": \"20000\"}}, \"const_declarations\": [{\"type\": \"linear\", \"direction\": \"budget\", \"limit\": \"30000\", \"terms\": {\"mall\": \"5000\", \"bus stop\": \"1000\", \"theatre\": \"3000\"}, \"operator\": \"LESS_OR_EQUAL\"}, {\"type\": \"upperbound\", \"direction\": \"limits the number\", \"limit\": \"20\", \"var\": \"bus stop\", \"operator\": \"LESS_OR_EQUAL\"}, {\"type\": \"ratio\", \"direction\": \"at most\", \"limit\": \"third\", \"var\": \"theatres\", \"operator\": \"LESS_OR_EQUAL\"}, {\"type\": \"ratio\", \"direction\": \"minimum\", \"limit\": \"20%\", \"var\": \"malls\", \"operator\": \"GREATER_OR_EQUAL\"}]}}"
            },
            {
                "role": "assistant",
                "content": "Variables:\n- x: Number of ads in malls\n- y: Number of ads at bus stops\n- z: Number of ads in theatres\n\nObjective:\n- Maximize viewership: 50000x + 10000y + 20000z\n\nConstraints:\n- The total cost of ads must not exceed the budget of $30000: 5000x + 1000y + 3000z <= 30000\n- The number of ads at a bus stop must be limited to 20: y <= 20\n- At most a third of the total number of ads should be in theatres: z <= 1/3(x + y + z), or: z <= 1/3x + 1/3y + 1/3z\n- At least 20% of ads should be in malls: x >= 0.2(x + y + z), or: x >= 0.2x + 0.2y + 0.2z\n\nFormulation:\nMaximize: 50000x + 10000y + 20000z\nConstraints:\n5000x + 1000y + 3000z <= 30000\ny <= 20\nz <= 1/3x + 1/3y + 1/3z\nx >= 0.2x + 0.2y + 0.2z"
            },
            {
                "role": "user",
                "content": "{\"-530221061\": {\"document\": \"A hedge fund is attempting to determine where its assets should be invested during the current year. At present, $3,200,000 is available for investment in stocks, options, security swaps, and futures. The annual rate of return on each type of investment is known to be: stocks, 11%; options, 30%; security swaps, 5%; futures, 15%. To ensure that the hedge fund\\u2019s portfolio is not too risky, the hedge fund\\u2019s investment manager has placed the following three restrictions on the hedge fund\\u2019s portfolio: a The amount invested in futures cannot exceed the amount invested in stocks. b At most 35% of the total amount invested may be in futures. c The amount invested in options cannot exceed the amount invested in security swaps.  The hedge fund\\u2019s objective is to maximize the annual return on its investment portfolio. Formulate an LP that will enable the hedge fund to meet this goal.\", \"order_mapping\": {\"stocks\": 0, \"options\": 1, \"security swaps\": 2, \"futures\": 3}, \"obj_declaration\": {\"type\": \"objective\", \"direction\": \"maximize\", \"name\": \"return\", \"terms\": {\"stocks\": \"11%\", \"options\": \"30%\", \"security swaps\": \"5%\", \"futures\": \"15%\"}}, \"const_declarations\": [{\"type\": \"xy\", \"x_var\": \"futures\", \"direction\": \"cannot exceed\", \"y_var\": \"stocks\", \"operator\": \"LESS_OR_EQUAL\"}, {\"type\": \"ratio\", \"direction\": \"At most\", \"limit\": \"35%\", \"var\": \"futures\", \"operator\": \"LESS_OR_EQUAL\"}, {\"type\": \"xy\", \"x_var\": \"options\", \"direction\": \"cannot exceed\", \"y_var\": \"security swaps\", \"operator\": \"LESS_OR_EQUAL\"}, {\"type\": \"sum\", \"direction\": \"available\", \"limit\": \"3,200,000\", \"operator\": \"LESS_OR_EQUAL\"}]}}"
            },
            {
                "role": "assistant",
                "content": "Variables:\n- x: Amount invested in stocks\n- y: Amount invested in options\n- z: Amount invested in security swaps\n- w: Amount invested in futures\n\nObjective:\n- Maximize the annual return: 0.11x + 0.30y + 0.05z + 0.15w\n\nConstraints:\n- The amount invested in futures cannot exceed the amount invested in stocks: w <= x\n- At most 35% of the total amount invested may be in futures: w <= 0.35(x + y + z + w), or: w <= 0.35x + 0.35y + 0.35z + 0.35w\n- The amount invested in options cannot exceed the amount invested in security swaps: y <= z\n- The total amount invested cannot exceed $3,200,000: x + y + z + w <= 3200000\n\nFormulation:\nMaximize: 0.11x + 0.30y + 0.05z + 0.15w\nConstraints:\nw <= x\nw <= 0.35x + 0.35y + 0.35z + 0.35w\ny <= z\nx + y + z + w <= 3200000"
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        model=MODEL, temperature=0, max_tokens=4000, top_p=0, frequency_penalty=0, presence_penalty=0)

    print(response)
    return response.choices[0].message.content


new_file = open('../../data/nl4opt/train_reduced_with_explanations.jsonl', 'w')

with jsonlines.open('../../data/nl4opt/train_reduced.jsonl') as reader:
    for line in reader.iter():
        print(str(line))
        explanation = call_gpt(str(line))
        # print(explanation)
        line['explanation'] = explanation
        new_file.write(json.dumps(line))
        new_file.write('\n')
        # break
