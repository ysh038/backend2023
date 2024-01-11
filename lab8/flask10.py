from http import HTTPStatus

from flask import Flask
from flask import make_response
from flask import request

app = Flask(__name__)


@app.route("/<num1>/<operator>/<num2>")
def calc_get(num1, operator, num2):
    arg1 = int(num1)
    operator = operator
    arg2 = int(num2)

    if operator == "+":
        result = arg1 + arg2
    elif operator == "*":
        result = arg1 * arg2
    else:
        result = arg1 - arg2

    resp = make_response(f"result is {result}!", HTTPStatus.OK)
    return resp


@app.route("/", methods=["POST"])
def calc_post():
    response_body = request.get_json()
    try:
        arg1 = int(response_body.get("arg1", "NO_ARG"))
        operator = response_body.get("op", "NO_OP")
        arg2 = int(response_body.get("arg2", "NO_ARG"))
    except:
        resp = make_response(f"bad request!", HTTPStatus.BAD_REQUEST)
        return resp

    if arg1 == "NO_ARG" or arg2 == "NO_ARG":
        resp = make_response(f"bad request!", HTTPStatus.BAD_REQUEST)
        return resp
    elif operator == "+":
        result = arg1 + arg2
    elif operator == "*":
        result = arg1 * arg2
    elif operator == "-":
        result = arg1 - arg2
    else:
        resp = make_response(f"bad request!", HTTPStatus.BAD_REQUEST)
        return resp
    resp = make_response(f"result is {result}!", HTTPStatus.OK)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=19123)
