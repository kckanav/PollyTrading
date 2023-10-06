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


def inform_user(msg, is_li = False):
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

    client.messages.create(
        from_= 'whatsapp:+14155238886',
        body=to_ret,
        to=kanav_number
    )
    logger.info(f"User Communication: {f'{len(msg)} alert(s) sent' if is_li else msg}")


def inform_admin(msg):
    logger.info(f"Admin communication: {msg}")
    client.messages.create(
        from_= 'whatsapp:+14155238886',
        body=msg,
        to=kanav_number
    )
