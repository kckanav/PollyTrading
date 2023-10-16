import logging
import os
from twilio.rest import Client

import constants

account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(constants.RUNTIME_LOG_FILE)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


kanav_number = 'whatsapp:+919811302691'
polly_number = 'whatsapp:+919268022112'


# TODO :- Need proper error handling. 

def inform_user(msg, is_li = False):
    total_alerts = len(msg)
    msg = format_message(msg, is_li=is_li)
    client.messages.create(
        from_= 'whatsapp:+14155238886',
        body=msg,
        to=polly_number
    )
    logger.info(f"User Communication: {f'{total_alerts} alert(s) sent' if is_li else msg}")

def format_message(msg, is_li = False):
    to_ret = msg
    if is_li:
        str_build = ""
        count = 0
        for m in msg:
            if count != 0:
                str_build += "\n"
            str_build += m
            count += 1
        to_ret = str_build
    return to_ret


def inform_admin(msg):
    client.messages.create(
        from_= 'whatsapp:+14155238886',
        body=msg,
        to=kanav_number
    )
    logger.info(f"Admin communication: {msg}")
