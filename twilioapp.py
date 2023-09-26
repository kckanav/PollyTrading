import webbrowser

from flask import Flask
import logging
from api import zerodha

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

@app.route("/")
def index():
    data = {"hi": "Congdfsas55555ations, it's a web app!"}
    return data


@app.route('/login')
def login():
    print(zerodha.login_url())
    return "bye"


@app.route("/auth")
def auth():
    request_token = request.args.get("request_token")
    if zerodha.zerodha_web_login(request_token):
        return this_data({
            "status": 200, "data": "Logged In!"
        })
    else:
        return this_data({
            "status": 400, "data": "Invalid Request Token"
        })


if __name__ == "__main__":
    app.run()