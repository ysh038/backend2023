from http import HTTPStatus

from flask import Flask
from flask import make_response
from flask import request

app = Flask(__name__)

@app.route('/<num1>/<operator>/<num2>')
def calc_get(num1,operator,num2):
    arg1 = int(num1)
    operator = operator
    arg2 = int(num2)

    if operator == "+":
        result = arg1 + arg2
    elif operator == "*":
        result = arg1 * arg2
    else:
        result = arg1 - arg2
        
    resp = make_response(f'result is {result}!',HTTPStatus.OK)
    return resp

@app.route('/',methods=['POST'])
def calc_post():
    response_body = request.get_json()
    arg1 = int(response_body["arg1"])
    operator = response_body["op"]
    arg2 = int(response_body["arg2"])

    if operator == "+":
        result = arg1+arg2
    elif operator == "*":
        result = arg1*arg2
    else:
        result = arg1-arg2

    resp = make_response(f'result is {result}!',HTTPStatus.OK)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=19123)