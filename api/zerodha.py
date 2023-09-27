import datetime
from urllib.parse import urlparse, parse_qs
from daily_prep import constants
from util.symbol import Symbol
from kiteconnect import KiteConnect, exceptions
import json
import webbrowser
import logging
import os

ZER_SYMBOL_NAME = "name"
ZER_LOT_SIZE = "lot_size"
ZER_INSTRUMENT_TOKEN = "instrument_token"
ZER_EXCHANGE = "exchange"
ZER_TRADING_SYMBOL = "tradingsymbol"
ZER_STRIKE = 'strike'
ZER_EXPIRY = 'expiry'
ZER_SEGMENT = 'segment'
ZER_FUTURE_SEGMENT = "NFO-FUT"

LOG_FILE_NAME = "/home/ubuntu/pollytrading/api/daily_files/" + datetime.date.today().isoformat() + "_log_file.log"
CREDENTIALS_FILE = constants.CREDENTIALS_DIRECTORY + constants.TODAY_CREDENTIALS_FILE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE_NAME)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



def get_instrument_codes():
    """
    This method fetches all the instrument codes for the symbols we need.

    CURRENT FILTRATION :--
        Currently, we fetch futures (EXCHANGE_NFO)
        We filter with strike == 0 and expiry == EXPIRY_DATE or EXPIRY_DATE_2 and segment == "NFO_FUT"

    :return: list with filtered symbols. Each symbol contains instrument_code and name.
    """
    kc = get_kiteconnect_instance()
    all_instruments_list = kc.instruments(kc.EXCHANGE_NFO)
    ret_instruments_list = []
    for instrument in all_instruments_list:
        if instrument[ZER_STRIKE] == 0 and (instrument[ZER_EXPIRY] == constants.EXPIRY_DATE or instrument[
            ZER_EXPIRY] == constants.EXPIRY_DATE_2) and instrument[ZER_SEGMENT] == ZER_FUTURE_SEGMENT:
            ret_instruments_list.append(instrument)

    logger.info("Instrument Codes Extracted for {} symbols through API".format(len(ret_instruments_list)))
    return ret_instruments_list


def get_kiteconnect_instance():
    """
    Returns a KiteConnect instance using the file "daily_prep/YYYY-MM-DD_connect_codes.json
    :return: A connected and live KiteConnect instance
    """
    with open(CREDENTIALS_FILE, 'r') as f:
        access_token = json.load(f)[0]
        kc = KiteConnect(os.environ["ZERODHA_API_KEY"], access_token)
        logger.info("KiteConnect instance created")
        return kc


def login_url():
    kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    return kc.login_url()


def login_with_request_token(request_token):
    """
    This method executes the login procedure through zerodha.py. It creates a file,
    daily_prep/"YYYY-MM-DD" + "_connect_codes.json", which has [api_key, api_secret, access_key]
    stored in it.


    FILE CREATED :- daily_prep/"YYYY-MM-DD" + "_connect_codes.json"
    FILE FORMAT :- [api_key, api_secret, access_key] (extract through JSON)
    USER :- Run the method. Login into Zerodha. Paste the redirected URL here.
    """

    kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    print(request_token)

    kc.generate_session(request_token, os.environ["ZERODHA_API_SECRET"])
    print("Login Sucessful! \n Welcome {}".format(kc.profile()['user_name']))

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump([kc.access_token], f)
    logger.info("Access Token created and stored")

    # try:
    #     kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    #     print(request_token)

    #     kc.generate_session(request_token, os.environ["ZERODHA_API_SECRET"])
    #     print("Login Sucessful! \n Welcome {}".format(kc.profile()['user_name']))

    #     with open(CREDENTIALS_FILE, "w") as f:
    #         json.dump([kc.access_token], f)
    #     logger.info("Access Token created and stored")

    # except KeyError:
    #     logger.error("Could not find zerodha environment variables")
    #     return 500, 'Zerodha credentials not set'

    # except exceptions.KiteException:
    #     logger.error("KiteException")
    #     return 500, 'Kite Internal Error'

    # except exceptions.TokenException:
    #     logger.error("Invalid Request Token entered")
    #     return 500, 'Request Token is invalid or has expired.'

    # return 200, 'Logged In'

