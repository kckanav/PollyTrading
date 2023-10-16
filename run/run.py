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

    instrument_list_for_zerodha = []
    instrument_token_to_name_map = dict()

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
        
        instrument_string = hist_symbol.zerodha_info[zerodha.ZER_EXCHANGE] + ":" + hist_symbol.zerodha_info[zerodha.ZER_TRADING_SYMBOL]
        instrument_list_for_zerodha.append(instrument_string)
        instrument_token_to_name_map[hist_symbol.zerodha_info[zerodha.ZER_INSTRUMENT_TOKEN]] = hist_symbol

        del api_dict[hist_symbol.name]

    for left_symbols in api_dict:
        logging.warning(f"Did not find {left_symbols} symbol in historical data file")

    return hist_li, instrument_list_for_zerodha, instrument_token_to_name_map


def run(time_delay = constants.TIME_INTERVAL, quantity_delta_perc = constants.D_QTY_PERCENTAGE_ALERT):

    count = 0
    try:
        logger.info(f"Starting The Cyclic Application with alert at {quantity_delta_perc * 100}% every {time_delay / 60} min")
        whatsapp.inform_user(f"Starting PollyTrading. \n D-QTY = {quantity_delta_perc * 100}% | Time = {time_delay / 60} min")
        whatsapp.inform_admin(f"Starting PollyTrading. \n D-QTY = {quantity_delta_perc * 100}% | Time = {time_delay / 60} min")


        all_symbols_list, instrument_list_for_zerodha, instrument_token_to_name_map = prepare(filter)
        kite = zerodha.get_kiteconnect_instance()
        whatsapp.inform_user("Setup complete!!")
        whatsapp.inform_admin("Setup complete!!")

        while True:
            try:
                alerts = []
                current_quotes = zerodha.quote(instrument_list_for_zerodha, instance = kite)
                for q in current_quotes:
                    quote = current_quotes[q]
                    symbol = instrument_token_to_name_map[quote[zerodha.ZER_INSTRUMENT_TOKEN]]
                    qtyrule.update(symbol, quote, quantity_delta_perc)
                    if symbol.actionable:
                        alerts.append(symbol)
                if count == 0:
                    whatsapp.inform_user("Application was started")
                    whatsapp.inform_admin("Application was started")
                    count += 1
                else:
                    if len(alerts) == 0:
                        whatsapp.inform_user("Updated. No Tradeable actions found.")
                    else:
                        message = msg_string_helper(alerts)
                        whatsapp.inform_user(message, is_li = True)
                        whatsapp.inform_admin("something was found")

                excelwriter.write_to_trade(all_symbols_list)
                logger.info("Successfully written at {}".format(datetime.datetime.now()))
                time.sleep(time_delay)
            except KeyboardInterrupt:
                logger.critical("Application Stopped")
                whatsapp.inform_user("Stopped Succesfully")
                whatsapp.inform_admin("The application was stopped")

            except Exception as e:
                whatsapp.inform_admin(f"Error :- {e}")
                continue

    except Exception as e:
        whatsapp.inform_admin(f"Something went wrong :- \n {e}")
        logger.critical(f"Error while running application at run number {count}:- {e}")


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
            "Diff": f"{round(symbol.curr_data[symbol.PRICE_DIFF], 1)}",
        }

        msg = f"{symbol.name} :- "
        max_len = max([len(data) for data in data_points])
        initial_offset = 4
        table_offset = max_len + 4

        for data in data_points:
            msg += "\n" + (" " * initial_offset) + data + ":" + (" " * (table_offset - len(data))) + data_points[data]
        message_list.append(msg)
    
    logger.info(" ".join(message_list))

    return message_list


def filter(instrument):
    if instrument[zerodha.ZER_STRIKE] == 0 \
            and instrument[zerodha.ZER_EXPIRY] in [constants.EXPIRY_DATE, constants.EXPIRY_DATE_2] and \
            instrument[zerodha.ZER_SEGMENT] == zerodha.ZER_FUTURE_SEGMENT:
        return True


