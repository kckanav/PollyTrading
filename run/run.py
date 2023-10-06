import datetime
import constants

from history import excel_reader
from api import zerodha

from run.rules import qtyrule
from run.storage import excelwriter
from run.comm import whatsapp

import time
import logging


logger = logging.getLogger(__name__)
print(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(constants.RUNTIME_LOG_FILE)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def filter(instrument):
    if instrument[zerodha.ZER_STRIKE] == 0 \
            and instrument[zerodha.ZER_EXPIRY] in [constants.EXPIRY_DATE, constants.EXPIRY_DATE_2] and \
            instrument[zerodha.ZER_SEGMENT] == zerodha.ZER_FUTURE_SEGMENT:
        return True


def run():
    logger.info("Starting The Cyclic Application")
    whatsapp.inform_user("PollyTrading has been started.")

    all_symbols_list = prepare(filter)
    whatsapp.inform_user("Setup complete!!")

    instrument_list_for_zerodha = []
    instrument_token_to_name_map = dict()

    for symbol in all_symbols_list:
        instrument_string = symbol.zerodha_info[zerodha.ZER_EXCHANGE] + ":" + symbol.zerodha_info[zerodha.ZER_TRADING_SYMBOL]
        instrument_list_for_zerodha.append(instrument_string)
        instrument_token_to_name_map[symbol.zerodha_info[zerodha.ZER_INSTRUMENT_TOKEN]] = symbol

    kite = zerodha.get_kiteconnect_instance()

    count = 0

    while True:
        alerts = []
        current_quotes = zerodha.quote(instrument_list_for_zerodha, instance = kite)
        for q in current_quotes:
            quote = current_quotes[q]
            symbol = instrument_token_to_name_map[quote[zerodha.ZER_INSTRUMENT_TOKEN]]
            alerts = qtyrule.update(symbol, quote)

        if count == 0:
            count += 1
        else:
            if len(alerts) == 0:
                whatsapp.inform_user("Updated! No Tradeable Actions Found :(")
            else:
                message = msg_string_helper(alerts)
                whatsapp.inform_user(message, is_li = True)

        excelwriter.write_to_trade(all_symbols_list)
        logger.info("Successfully written at {}".format(datetime.datetime.now()))
        time.sleep(10)


def msg_string_helper(actionable_symbols):
    message_list = []
    for symbol in actionable_symbols:
        data_points = {
            "D.QTY": f"{round(symbol.curr_data[symbol.QTY_DELTA] * 100, 2)}%",
            "No. of Chaal": f"{symbol.curr_data[symbol.NUMBER_OF_TICKS]}",
            "% Top-3" : f"{round(symbol.curr_data[symbol.TOP_3_DELTA]* 100, 2)}%",
            "% O.Cost": f"{round(symbol.curr_data[symbol.O_COST_DELTA]* 100, 2)}%",
            "% Cost": f"{round(symbol.curr_data[symbol.COST_DELTA ] * 100, 2)}%",
            "% Avg": f"{round(symbol.curr_data[symbol.AVG_DELTA] * 100, 2)}%",
            "Net Avg Price": f"{round(symbol.curr_data[symbol.CURRENT_PRICE], 2)}",
            "Diff": f"{round(symbol.curr_data[symbol.CURRENT_PRICE], 2)}",
        }
        logger.info(f"   Found one at {symbol.name} with D.QTY = {round(symbol.curr_data[symbol.QTY_DELTA] * 100, 2)}%")
        msg = f"{symbol.name} :- \n"
        for data in data_points:
            msg += "   " + data + ":- " + data_points[data] + "\n"
        message_list.append(msg)
        return message_list



def prepare(filter):

    api_li = zerodha.get_instrument_codes(filter)
    api_dict = {instrument[zerodha.ZER_SYMBOL_NAME]: instrument for instrument in api_li}

    hist_li = excel_reader.load_all_symbols(constants.HISTORY_USER_UPLOADED_FILE)

    for hist_symbol in hist_li:

        curr_api_info = api_dict[hist_symbol.name]
        hist_symbol.zerodha_info = curr_api_info

        h_lot_size = hist_symbol.data[hist_symbol.LOT_SIZE]
        z_lot_size = curr_api_info[zerodha.ZER_LOT_SIZE]

        if not h_lot_size == z_lot_size:
            # We have found a mismatch in lot size between DATA-$ file and Zerodha.
            logger.warning(
                f"Lot Size Mismatch! {hist_symbol.name}. Zerodha = {z_lot_size} != {h_lot_size} = History File. "
                f"Using {z_lot_size}")
            hist_symbol.data[hist_symbol.LOT_SIZE] = curr_api_info[zerodha.ZER_LOT_SIZE]

        del api_dict[hist_symbol.name]

    for left_symbols in api_dict:
        logging.warning(f"Did not find {left_symbols} symbol in historical data file")

    return hist_li
