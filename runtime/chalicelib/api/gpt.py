import leangle
import openai
import json
from chalice import Blueprint

from ..authorizer import token_auth

gpt_routes = Blueprint(__name__)

@leangle.describe.tags(["GPT-3"])
@leangle.describe.response(204, description='Stocks')
@gpt_routes.route('/{api_call}', methods=['GET'], cors=True)
def update_stocks(api_call):
    print(api_call)
    db = ''
    with open('./chalicelib/api/db_state.json', 'r') as f:
        db = json.load(f)

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=make_prompt(db, api_call),
        temperature=0.6,
        max_tokens=500
    )
    main_result = response.choices[0].text
    res = main_result.replace("'", '"')
    with open('./chalicelib/api/db_state.json', 'w') as f:
        f.write(res)
    return res


def make_prompt(db, api_call):
    return """
This is the current database state:
{}

This is the desired command:
{}

Now return what the database should look like after executing the command, 
respecting the json schema of the current DB state.
""".format(
        db,
        api_call
    )