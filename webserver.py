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
file_handler = logging.FileHandler('server.log')
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)

current_state = {
    'isFileUploaded': False, 'isLoggedIn': False, 'error_message': "", 'recent_file_name': None,
    'application_running': False, 'pid': 0, "process": None, "last_uploaded_file": constants.latest_uploaded_file()
}

count = {"count": 0}

bye = 0


@app.route("/")
def index():
    current_state['isLoggedIn'] = zerodha.logged_in()

    file_name= constants.latest_runtime_trade_file().split("-")
    current_state['recent_file_name'] = file_name[-1]

    last_uploaded_file = constants.latest_uploaded_file().split("/")
    current_state['last_uploaded_file'] = last_uploaded_file[-1]
    return render_template("index.html", data = current_state)


@app.route('/login_url')
def login_url():
    print(zerodha.login_url())
    logger.debug("Login URL requested")
    return zerodha.login_url()


@app.route('/login')
def login():
    print(zerodha.login_url())
    logger.debug("Redirecting to Login URL")
    return redirect(zerodha.login_url())


@app.route('/upload_file', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return redirect("/")
    else:
        f = request.files['file']
        if f.filename != '':
            f.save(constants.HISTORY_FILE_UPLOAD_DIRECTORY + f.filename)

    return redirect("/")


@app.route('/download_trade')
def download():
    return send_file(constants.latest_runtime_trade_file(), as_attachment = True)


@app.route("/auth")
def auth():
    request_token = request.args.get("request_token")
    code, msg = zerodha.login_with_request_token(request_token)

    if code == 200:
        current_state['isLoggedIn'] = True
    else:
        current_state['error_message'] = msg

    return redirect("/")


@app.route("/start_app", methods = ["POST"])
def start_app():
    request.args.get('d_qty')
    d_qty = request.form.get('d_qty', constants.D_QTY_PERCENTAGE_ALERT)
    time_interval = request.form.get('time_interval', constants.TIME_INTERVAL)
    start_application(d_qty = d_qty, time_interval = time_interval)
    return redirect("/")

@app.route("/stop_app")
def stop_app():
    stop_application()
    return redirect("/")


@app.route("/msg", methods = ['GET', 'POST'])
def msg():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    body = request.values.get('Body', None)
    resp = MessagingResponse()

    if body.lower() == 'start':
        # TODO : Start with inital condiations provided. Like, "start 6% 5min"
        resp.message("Okay")
        start_application()
    elif body.lower() in ["stop", 'end', 'kill'] and current_state['pid'] != 0:
        resp.message("Stopping")
        stop_application()
    else:
        resp.message("Invalid Request")
    return str(resp)


# TODO :- Error Handling, Logging
def start_application(d_qty = constants.D_QTY_PERCENTAGE_ALERT, time_interval = constants.TIME_INTERVAL):
    try:
        path = os.environ["CONDA_PREFIX"]
    except KeyError:
        logger.debug("not conda")
        path = {os.environ["VIRTUAL_ENV"]}

    k = subprocess.Popen([f'{path}/bin/python3.10', f'start_application.py', str(d_qty), str(time_interval)], stdin = subprocess.DEVNULL,
                         stdout = open('nohup_test.out', 'a'), stderr = subprocess.STDOUT, start_new_session = True,
                         preexec_fn = (lambda: signal.signal(signal.SIGHUP, signal.SIG_IGN)))
    current_state['application_running'] = True
    current_state['process'] = k
    current_state['pid'] = k.pid


def stop_application():
    os.kill(current_state['pid'], signal.SIGINT)
    current_state['application_running'] = False
    current_state['pid'] = 0


def this_data(data):
    return data


if __name__ == "__main__":
    app.run(host = "localhost", port = 5001)
