import os
import webbrowser

from flask import Flask, request, render_template, flash, redirect, send_file
import logging


from twilio.twiml.messaging_response import MessagingResponse, Message

from api import zerodha
from history import history
from run import run
import constants
import subprocess, signal


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)

current_state = {
  'isFileUploaded': False,
  'isLoggedIn': False,
  'error_message': "",
  'application_running': False,
  'pid': 0
}

@app.route("/")
def index():
  current_state['isLoggedIn'] = zerodha.logged_in()
  current_state['isFileUploaded'] = history.is_file_generated()
  return render_template("index.html", data=current_state)


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
    return redirect("/")
  else:  
    f = request.files['file']
    if f.filename != '':
      f.save(constants.HISTORY_FILE_UPLOAD_DIRECTORY + f.filename)
      history.save_and_return_history(in_file = f, marker = history.DATA_FILE_MARKER)
      current_state['isFileUploaded'] = True

  return redirect("/")

@app.route('/download_trade')
def download():
  return send_file(constants.RUNTIME_GENERATED_FILE, as_attachment=True)


@app.route("/auth")
def auth():

    request_token = request.args.get("request_token")
    code, msg = zerodha.login_with_request_token(request_token)

    if code == 200:
      current_state['isLoggedIn'] = True
    else:
      current_state['error_message'] = msg

    return redirect("/")


@app.route("/ins")
def ins_list():
  return zerodha.get_instrument_codes()


@app.route("/msg",  methods = ['GET', 'POST'])
def msg():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    body = request.values.get('Body', None)
    resp = MessagingResponse()

    if body.lower() == 'start':
        resp.message("Okay")
        k = subprocess.Popen(['polly_env/bin/python', 'start_application.py'], stdin = subprocess.DEVNULL,
                             stdout = open('nohup_test.out', 'w'), stderr = subprocess.STDOUT, start_new_session = True,
                             preexec_fn = (lambda: signal.signal(signal.SIGHUP, signal.SIG_IGN)))

        current_state['application_running'] = True
        current_state['pid'] = k.pid
    elif body.lower() in ["stop", 'end', 'kill'] and current_state['pid'] != 0:
        resp.message("Stopping")
        os.kill(current_state['pid'], signal.SIGINT)
        current_state['application_running'] = False
        current_state['pid'] = 0
    else:
        resp.message("Invalid Request")
    return str(resp)


# @app.route('/start')
# def start():
#   th = Thread(target = run.run)
#   th.start()
#   return "application started"


def this_data(data):
  return data


if __name__ == "__main__":
    app.run(host = "localhost", port = 5001)