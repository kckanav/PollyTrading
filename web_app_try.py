import webbrowser

import flask

from api import zerodha
from flask import Flask
import logging
from flask import request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)


@app.route("/")
def index():
    data = {"hi": "Congratulations, it's a web app!"}
    return this_data(data)


@app.route("/login_url")
def url():
    return this_data({"url": zerodha.login_url()})


@app.route("/auth")
def login():
    request_token = request.args.get("request_token")
    if zerodha.zerodha_web_login(request_token):
        return this_data({
            "status": 200, "data": "Logged In!"
        })
    else:
        return this_data({
            "status": 400, "data": "Invalid Request Token"
        })


@app.route("/connected")
def connected():
    kc = zerodha.get_kiteconnect_instance()
    return this_data({"status": 200, "data": kc.profile()})


def this_data(data):
    response = flask.jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = 8080, debug = True)  # zerodha.login()  # setup.populate_symbols()

# app = Flask(__name__)
#
# @app.route("/")
# def index():
#     celsius = request.args.get("celsius", "")
#     return (
#         """<form action="" method="get">
#                 <input type="text" name="celsius">
#                 <input type="submit" value="Convert">
#             </form>"""
#         + celsius
#     )
#
#
#
# @app.route("/<int:celsius>")
# def fahrenheit_from(celsius):
#     """Convert Celsius to Fahrenheit degrees."""
#     fahrenheit = float(celsius) * 9 / 5 + 32
#     fahrenheit = round(fahrenheit, 3)  # Round to three decimal places
#     return str(fahrenheit)
#
# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8080, debug=True)
