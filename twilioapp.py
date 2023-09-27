import webbrowser

from flask import Flask, request, render_template, flash, redirect
import logging
from api import zerodha
from history import history
from run import run
from threading import Thread


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = '/home/ubuntu/pollytrading/history/daily_files/historical_data/'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    data = {"hi": "Congdfsas55555ations, it's a web app!"}
    return data


@app.route('/login_url')
def login_url():
    print(zerodha.login_url())
    return zerodha.login_url()


@app.route('/login')
def login():
    print(zerodha.login_url())
    return redirect(zerodha.login_url())


@app.route('/upload_file', methods = ['GET', 'POST'])
def upload_file():
  if request.method == 'GET':
    return render_template("upload.html")
  else:  
    f = request.files['file']
    if f.filename == '':
      flash('No selected file')
      return render_template("upload.html")
    else:
      f.save(app.config['UPLOAD_FOLDER'] + f.filename)
      history.save_and_return_history(in_file = f, marker = history.DATA_FILE_MARKER)
      return render_template("ack_upload.html", name = f.filename)  


@app.route("/auth")
def auth():
    request_token = request.args.get("request_token")
    code, msg = zerodha.login_with_request_token(request_token)
    if code == 200:
        return this_data({
            "status": 200, "data": "Logged In!"
        })
    else:
        return this_data({
            "status": code, "data": msg
        })

@app.route("/ins")
def ins_list():
  return zerodha.get_instrument_codes()


# @app.route('/start')
# def start():
#   th = Thread(target = run.run)
#   th.start()
#   return "application started"


def this_data(data):
  return data


if __name__ == "__main__":
    app.run()