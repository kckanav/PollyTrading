# external packages
from history import excel_reader
from api import zerodha

# Runtime packages
from run.rules import qtyrule
from run.storage import excelwriter
from run.comm import whatsapp

# utils
import time
import logging
import datetime
import constants


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(constants.RUNTIME_LOG_FILE)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def prepare(token_list_filter):

    api_li = zerodha.get_instrument_codes(token_list_filter)
    api_dict = {instrument[zerodha.ZER_SYMBOL_NAME]: instrument for instrument in api_li}

    hist_li = excel_reader.load_all_symbols(constants.latest_uploaded_file())

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


def run(time_delay = constants.TIME_INTERVAL, quantity_delta_perc = constants.D_QTY_PERCENTAGE_ALERT):
    try:
        logger.info(f"Starting The Cyclic Application with alert at {quantity_delta_perc * 100}% every {time_delay / 60} min")
        whatsapp.inform_user(f"PollyTrading has been started. \n D-QTY = {quantity_delta_perc * 100}% | Time = {time_delay / 60} min")
        whatsapp.inform_admin("Application was started")

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
                qtyrule.update(symbol, quote, quantity_delta_perc)
                if symbol.actionable:
                    alerts.append(symbol)

            if count == 0:
                count += 1
            else:
                if len(alerts) == 0:
                    whatsapp.inform_user("Updated! No actionable symbol found.")
                else:
                    message = msg_string_helper(alerts)
                    whatsapp.inform_user(message, is_li = True)

            excelwriter.write_to_trade(all_symbols_list)
            logger.info("Successfully written at {}".format(datetime.datetime.now()))
            time.sleep(time_delay)
    except KeyboardInterrupt:
        whatsapp.inform_user("Stopped Succesfully")
        whatsapp.inform_admin("The application was stopped")
    except Exception as e:
        whatsapp.inform_admin(f"Something went wrong :- \n {e}")


def msg_string_helper(actionable_symbols):
    message_list = []
    for symbol in actionable_symbols:
        data_points = {
            "Chaal No.": f"{symbol.curr_data[symbol.NUMBER_OF_TICKS]}",
            "D.QTY": f"{round(symbol.curr_data[symbol.QTY_DELTA] * 100, 1)}%",
            "Top-3" : f"{round(symbol.curr_data[symbol.TOP_3_DELTA]* 100, 1)}%",
            "O.Cost": f"{round(symbol.curr_data[symbol.O_COST_DELTA]* 100, 1)}%",
            "Cost": f"{round(symbol.curr_data[symbol.COST_DELTA ] * 100, 1)}%",
            "Avg": f"{round(symbol.curr_data[symbol.AVG_DELTA] * 100, 1)}%",
            "Current": f"{round(symbol.curr_data[symbol.CURRENT_PRICE], 1)}",
            "Diff": f"{round(symbol.curr_data[symbol.CURRENT_PRICE], 1)}",
        }

        msg = f"{symbol.name} :- \n"
        max_len = max([len(data) for data in data_points])
        initial_offset = 4
        table_offset = max_len + 4

        for data in data_points:
            msg += (" " * initial_offset) + data + ":" + (" " * (table_offset - len(data))) + data_points[data] + "\n"
        message_list.append(msg)
        logger.info(" ".join(message_list))
        return message_list


def filter(instrument):
    if instrument[zerodha.ZER_STRIKE] == 0 \
            and instrument[zerodha.ZER_EXPIRY] in [constants.EXPIRY_DATE, constants.EXPIRY_DATE_2] and \
            instrument[zerodha.ZER_SEGMENT] == zerodha.ZER_FUTURE_SEGMENT:
        return True


