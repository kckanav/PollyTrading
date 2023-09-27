import logging

import api.zerodha
from api import zerodha
from history import history
import constants
from util.symbol import Symbol
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(constants.MORNING_PREP_LOG_FILE)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def get_prepared_data(filename=constants.MORNING_PREP_DATA_FILE):
    """
    Loads all symbols from {CONSTANTS.HIST_SYMBOL_DATA_DICT_FILE} which is dictonary of UNDERLYING_STOCK_NAME: Symbol
    :return: A list of Symbol objects. [Symbol, Symbol, ...]
    """
    try:
        with open(filename, 'r') as f:
            all_symbols_json = json.load(f)
            all_symbols_list = []
            for symbol in all_symbols_json:
                symbol = Symbol(my_dict = symbol)
                all_symbols_list.append(symbol)
        if len(all_symbols_list) != constants.USER_TOTAL_NUMBER_OF_SYMBOLS:
            logger.warning("Number of Symbols MISMATCH: Loaded Symbols = {} from {} | Expected = {} ".format(len(all_symbols_list),
                                                                                                             filename,
                                                                                                             constants.USER_TOTAL_NUMBER_OF_SYMBOLS))
        else:
            logger.info("Read {} symbols from {}".format(len(all_symbols_list), filename))

        return all_symbols_list

    except FileNotFoundError:
        return prepare(filename)


def prepare(filename=constants.MORNING_PREP_DATA_FILE):

    api_li = zerodha.get_instrument_codes()
    api_dict = create_symbols_with_api_info(api_li)

    hist_li = history.load_all_symbols()


    for hist_symbol in hist_li:

        curr_api_info = api_dict[hist_symbol.name]
        del api_dict[hist_symbol.name]

        hist_symbol.add_api_info(curr_api_info['needed_info'])

        if not hist_symbol.data['lot_size'] == curr_api_info['verification_info'][api.zerodha.ZER_LOT_SIZE]:
            # We have found a mismatch in lot size between STOCK-$ file and Zerodha.
            logger.warning("Lot Size Mismatch for {}. Zerodha = {} != {} = History File. Using {}".format(hist_symbol.name, curr_api_info['verification_info'][api.zerodha.ZER_LOT_SIZE],
                                                                     hist_symbol.data['lot_size'], curr_api_info['verification_info'][api.zerodha.ZER_LOT_SIZE]))
            hist_symbol.data['lot_size'] = curr_api_info['verification_info'][api.zerodha.ZER_LOT_SIZE]

    for left_symbols in api_dict:
        logging.warning("Did not find {} symbol in historical data file".format(left_symbols))

    with open(filename, 'w') as f:
        json.dump(hist_li, f, default = vars)
        logger.info("Historical Symbol Data file created at {}".format(filename))

    return hist_li


def create_symbols_with_api_info(instrument_codes_list):
    info_dict = dict()
    for instrument in instrument_codes_list:
        curr_symbol_name = instrument['name']
        info_dict[curr_symbol_name] = {
            'needed_info': {
                Symbol.TRADING_SYMBOL: instrument[zerodha.ZER_TRADING_SYMBOL],
                Symbol.INSTRUMENT_TOKEN: instrument[zerodha.ZER_INSTRUMENT_TOKEN],
                Symbol.EXCHANGE: instrument[zerodha.ZER_EXCHANGE]},
            'verification_info': instrument
        }
    return info_dict


if __name__ == '__main__':
    prepare()