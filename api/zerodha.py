import datetime
from urllib.parse import urlparse, parse_qs
from daily_prep import constants
from util.symbol import Symbol
from kiteconnect import KiteConnect
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE_NAME)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def create_symbols_with_api_info():
    instrument_codes_list = get_instrument_codes()
    api_info = dict()
    for instrument in instrument_codes_list:
        curr_symbol_name = instrument['name']
        api_info[curr_symbol_name] = {
            Symbol.TRADING_SYMBOL: instrument[ZER_TRADING_SYMBOL],
            Symbol.INSTRUMENT_TOKEN: instrument[ZER_INSTRUMENT_TOKEN],
            Symbol.EXCHANGE: instrument[ZER_EXCHANGE]
        }

    return api_info

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
    file_name = constants.CREDENTIALS_DIRECTORY + constants.TODAY_CREDENTIALS_FILE

    try:
        with open(file_name, 'r') as f:
            api_key, api_secret, access_key = json.load(f)

        logger.info("KiteConnect instance created")
        return KiteConnect(api_key, access_key)

    # TODO: Add Invalid credentials/token so that they can login again.
    except FileNotFoundError:
        kc = login()
        logger.info("KiteConnect instance created")
        return kc


def login_url():
    kc = KiteConnect(constants.API_KEY)
    return kc.login_url()


def login(request_token = None):
    """
    This method executes the login procedure through zerodha.py. It creates a file,
    daily_prep/"YYYY-MM-DD" + "_connect_codes.json", which has [api_key, api_secret, access_key]
    stored in it.


    FILE CREATED :- daily_prep/"YYYY-MM-DD" + "_connect_codes.json"
    FILE FORMAT :- [api_key, api_secret, access_key] (extract through JSON)
    USER :- Run the method. Login into Zerodha. Paste the redirected URL here.
    """
    kc = KiteConnect(os.environ["ZERODHA_API_KEY"])
    if request_token is None:
        return None
    print(request_token)

    kc.generate_session(request_token, os.environ["ZERODHA_API_SECRET"])

    print("Login Sucessful! \n Welcome {}".format(kc.profile()['user_name']))

    file_name = constants.CREDENTIALS_DIRECTORY + constants.TODAY_CREDENTIALS_FILE
    with open(file_name, "w") as f:
        json.dump([constants.API_KEY, constants.API_SECRET, kc.access_token], f)

    logger.info("Access Token created and stored at {}".format(file_name))
    return kc


def zerodha_web_login(request_token):
    if request_token is None:
        return "Invalid Request Token"
    else:
        return login(request_token)


if __name__ == '__main__':
    create_symbols()

