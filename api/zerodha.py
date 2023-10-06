import datetime
import webbrowser
from urllib.parse import urlparse, parse_qs

import constants
from kiteconnect import KiteConnect, exceptions
import json
import logging
import os

ZER_SYMBOL_NAME = "name"
ZER_LOT_SIZE = "lot_size"
ZER_VOLUME = "volume"
ZER_INSTRUMENT_TOKEN = "instrument_token"
ZER_EXCHANGE = "exchange"
ZER_TRADING_SYMBOL = "tradingsymbol"
ZER_STRIKE = 'strike'
ZER_EXPIRY = 'expiry'
ZER_SEGMENT = 'segment'
ZER_FUTURE_SEGMENT = "NFO-FUT"
ZER_TIMESTAMP = "timestamp"
ZER_AVG_PRICE = "average_price"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(constants.ZERODHA_LOG_FILE)
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
    with open(constants.ZERODHA_CREDENTIALS_FILE, 'r') as f:
        access_token = json.load(f)[0]
        kc = KiteConnect(os.environ["ZERODHA_API_KEY"], access_token)
        logger.info("KiteConnect instance created")
        return kc


def login_with_terminal():
    """
    This method executes the login procedure through zerodha.py. It creates a file,
    daily_prep/"YYYY-MM-DD" + "_connect_codes.json", which has [api_key, api_secret, access_key]
    stored in it.


    FILE CREATED :- daily_prep/"YYYY-MM-DD" + "_connect_codes.json"
    FILE FORMAT :- [api_key, api_secret, access_key] (extract through JSON)
    USER :- Run the method. Login into Zerodha. Paste the redirected URL here.
    """
    kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    webbrowser.open_new_tab(kc.login_url())
    request_token_url = input("Please Enter request token url\n")
    parsed_url = urlparse(request_token_url)
    request_token = parse_qs(parsed_url.query)['request_token'][0]
    print(request_token)
    kc.generate_session(request_token, os.environ["ZERODHA_API_SECRET"])

    print("Login Sucessful! \n Welcome {}".format(kc.profile()['user_name']))

    with open(constants.ZERODHA_CREDENTIALS_FILE, "w") as f:
        json.dump([kc.access_token], f)

    logger.info("Access Token created and stored at {}".format(constants.ZERODHA_CREDENTIALS_FILE))
    return kc


def login_url():
    kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    logger.info("Possible login started")
    return kc.login_url()


def logged_in():
    try:
        kc = get_kiteconnect_instance()
        return True
    except (exceptions.KiteException, FileNotFoundError):
        print("here")
        return False


def login_with_request_token(request_token):
    """
    This method executes the login procedure through zerodha.py. It creates a file,
    daily_prep/"YYYY-MM-DD" + "_connect_codes.json", which has [api_key, api_secret, access_key]
    stored in it.


    FILE CREATED :- daily_prep/"YYYY-MM-DD" + "_connect_codes.json"
    FILE FORMAT :- [api_key, api_secret, access_key] (extract through JSON)
    USER :- Run the method. Login into Zerodha. Paste the redirected URL here.
    """

    # kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    # print(request_token)

    # kc.generate_session(request_token, os.environ["ZERODHA_API_SECRET"])
    # print("Login Sucessful! \n Welcome {}".format(kc.profile()['user_name']))

    # with open(constants.ZERODHA_CREDENTIALS_FILE, "w") as f:
    #     json.dump([kc.access_token], f)
    # logger.info("Access Token created and stored")


    try:
        kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
        print(request_token)

        kc.generate_session(request_token, os.environ["ZERODHA_API_SECRET"])
        print("Login Sucessful! \n Welcome {}".format(kc.profile()['user_name']))

        with open(constants.ZERODHA_CREDENTIALS_FILE, "w") as f:
            json.dump([kc.access_token], f)
        logger.info("Access Token created and stored")

    except KeyError as err:
        logger.error(err)
        return 1, 'Zerodha credentials not set. Please contact Kanav'

    except exceptions.TokenException as err:
        logger.error("Invalid Request Token entered")
        return 2, 'Please Log in Again'

    except exceptions.KiteException as err:
        logger.error(err)
        return 2, 'Please log in again in some time'



    return 200, 'Logged In'

if __name__ == '__main__':
    login_with_terminal()