import os
from twilio.rest import Client


account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

kanav_number = 'whatsapp:+919811302691'
polly_number = 'whatsapp:+919268022112'


def inform_user(msg, is_li = False):
    to_send = ""
    if is_li:
        for m in msg:
            to_send += m
            to_send += "\n"
        msg = to_send

    message = client.messages.create(
        from_= 'whatsapp:+14155238886',
        body=msg,
        to=kanav_number
    )


def inform_admin(msg):
    message = client.messages.create(
        from_= 'whatsapp:+14155238886',
        body=msg,
        to=kanav_number
    )