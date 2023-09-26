import api.zerodha
from daily_prep import constants
import json
import logging
from history import history
from util import fileio
from api import zerodha, keys


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(constants.TODAY_LOG_FILE)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

STOCK_FILENAME = constants.DATA_DIRECTORY + "STOCK-11.xlsx"
TRADE_FILENAME = constants.DATA_DIRECTORY + "TRADE-15.xlsx"
FILENAME = TRADE_FILENAME


# TODO : First traverse by historical data and then Instrument list to ensure we only have our symbols.
def populate_symbols():
    """
    This method extracts data from the STOCK-$.xslx file to get old_oi, cost, o-cost, o-avg data for each symbol,
    and then combines this data with the instrument lists from zerodha.py to create a symbol_dict that can be used
    to get market data from zerodha.py and compute it with historical data.

    Historical data (File I/O)               Zerodha Instruments List (API Call)
            |                                       |
                |                               |
                    |                       |
                        |               |
                            |       |
                             "SYMBOL"
                           fully filled
                                |
                                |
                           Data stored in
                    "HIST_SYMBOL_DATA_DICT_FILE"

    Assumptions :-
        1. 'name' field in Instruments API should match the "SYMBOL" in Stock-$.xslx
        2. STOCK-$.xslx is first sorted according to date, then 'cost' in Symbol_format
           is taken from 'Cost' in STOCK-$ for the latest date, and 'o_cost' in
           Symbol_format is taken from 'Cost' for the second latest day.
    """
    instrument_code_list = zerodha.get_instrument_codes()
    historical_data = history.load_all_symbols()

    for instrument in instrument_code_list:
        name = instrument[api.zerodha.ZER_SYMBOL_NAME]  # name from zerodha.py instrument api
        symbol = historical_data[name]

        # TODO: Proper logging here to indicate there is error in matching.
        # This is where data from excel and instruments is being merged.
        # -----------------Robust checking needed here ---------------
        if not symbol.name == name:
            # We have found a symbol which does not exist in STOCK-$.xlsx file
            logging.warning(
                "Zerodha:- {} != File :- {}.{} does not exist in {}. Ignoring this Symbol".format(name, symbol.name,
                                                                                                  name, FILENAME))
            assert symbol.name == name
        elif not symbol.data['lot_size'] == instrument[api.zerodha.ZER_LOT_SIZE]:
            # We have found a mismatch in lot size between STOCK-$ file and Zerodha.
            logging.warning(" {} does not have matching lot size \n    Zerodha lot size = {} \n    {} lot size "
                            "= {}. \n   Using Zerodha's Lot Size".format(name, instrument[api.zerodha.ZER_LOT_SIZE], FILENAME,
                                                                         symbol.data['lot_size']))
            symbol.data['lot_size'] = instrument[api.zerodha.ZER_LOT_SIZE]

        # ------------------------------------------------------------------------------

        symbol.zerodha_info['instrument_token'] = instrument[api.zerodha.ZER_INSTRUMENT_TOKEN]
        symbol.zerodha_info['exchange'] = instrument[api.zerodha.ZER_EXCHANGE]
        symbol.zerodha_info['trading_symbol'] = instrument[api.zerodha.ZER_TRADING_SYMBOL]

    file_name = constants.DATA_DIRECTORY + constants.HIST_SYMBOL_DATA_DICT_FILE
    with open(file_name, 'w') as f:
        json.dump(historical_data, f, default = vars)
        print("Historical Symbol Data file created at {}".format(file_name))

    return historical_data


def test():
    return 1
