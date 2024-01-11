from http import HTTPStatus

from flask import Flask
from flask import make_response

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!" + 1


@app.route("/bad", methods=["GET", "POST"])
def bad_world():
    return "Bad World!"


@app.route("/good")
def good_world():
    return "Good World!"


@app.route("/<greeting>/<name>")
def greet(greeting, name):
    resp = make_response(f"{greeting},{name}!", HTTPStatus.NOT_FOUND)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=19123)
