import datetime

from daily_prep import constants
from util.symbol import Symbol
from daily_prep import morning_routine
from api import zerodha
import time
import logging
import csv


LOG_FILE = "/Users/kanavgupta/Desktop/pollytrading/run/daily_files/" + datetime.date.today().isoformat() + "_log_file.log"
RUNNING_FILE = "/Users/kanavgupta/Desktop/pollytrading/run/daily_files/" + datetime.date.today().isoformat() + "_action_2.csv"

THRESHOLD = 0.10

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def write(symbols: [Symbol]):
    # field names
    fields = ['Timestamp', 'OLD OI', 'Lot', 'Top-3', 'O-Cost', 'Cost', 'O-Avg', 'Symbol', 'D.QTY', 'QTY', '% Top-3', '% O-Cost',
              '% Cost', '% Avg', 'Current', 'Diff', 'Actionable']

    rows = []
    for symbol in symbols:
        rows.append(symbol.gen_string_for_trade_xslx())

    # name of csv file
    filename = RUNNING_FILE

    # writing to csv file
    with open(filename, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(fields)

        # writing the data rows
        csvwriter.writerows(rows)
        csvwriter.writerow([])


def check_update(symbol, curr_vol, current_avg, timestamp):
    # ERROR HANDLING :-
    # 1. Because the previous volume stored is last trading days
    # Very Unexpected. Break program and report.
    error_message = "The volume stored for {} has not been updated. Please update all symbols" \
                    "by running setup.load_symbols using previous days data.\n" \
                    "Last Volume Stored :- {} vs Current Volume {}.".format(symbol.name,
                                                                            symbol.curr_data[symbol.LAST_VOL], curr_vol)
    assert curr_vol >= symbol.curr_data[symbol.LAST_VOL], error_message

    assert symbol.data[
               symbol.OLD_OI] is not None, "No OLD OPEN INTEREST stored for {}. Please update all symbols.".format(
        symbol.name)

    li = ['D.QTY', 'QTY', '% Top-3', '% O-Cost', '% Cost', '% Avg', 'Current', 'Diff']

    last_value = symbol.curr_data[symbol.LAST_VOL] * symbol.curr_data[symbol.LAST_AVG_PRICE]
    curr_value = current_avg * curr_vol
    curr_value_delta = curr_value - last_value

    curr_vol_delta = (curr_vol - symbol.curr_data[symbol.LAST_VOL])
    if curr_vol_delta != 0:
        current_price = curr_value_delta / curr_vol_delta
    else:
        # TODO :- These are the stocks that are banned, as they are not being traded
        #         It could also be that this stock had no trading.
        current_price = 0

    curr_qty = curr_vol_delta / symbol.data[symbol.LOT_SIZE]

    curr_quantity_delta = (curr_qty / symbol.data[symbol.OLD_OI])

    top_3_delta = ((current_price - symbol.data[symbol.TOP_3]) / (symbol.data[symbol.TOP_3]))

    old_cost_delta = (symbol.data[symbol.COST] - symbol.data[symbol.O_COST]) / symbol.data[symbol.O_COST]

    cost_delta = (current_price - symbol.data[symbol.COST]) / symbol.data[symbol.COST]

    avg_delta = (current_price - symbol.data[symbol.O_AVG]) / symbol.data[symbol.O_AVG]

    price_diff = current_price - symbol.curr_data[symbol.CURRENT_PRICE]

    if symbol.curr_data[symbol.LAST_VOL] != 0 and curr_quantity_delta >= THRESHOLD:
        symbol.actionable = True
        logger.info("   Found one at {} with D.QTY = {} ".format(symbol.name, curr_quantity_delta))
        symbol.curr_data[symbol.NUMBER_OF_TICKS] += 1
    else:
        symbol.actionable = False

    symbol.curr_data[symbol.QTY] = curr_qty
    symbol.curr_data[symbol.QTY_DELTA] = curr_quantity_delta
    symbol.curr_data[symbol.TOP_3_DELTA] = top_3_delta
    symbol.curr_data[symbol.O_COST_DELTA] = old_cost_delta
    symbol.curr_data[symbol.COST_DELTA] = cost_delta
    symbol.curr_data[symbol.AVG_DELTA] = avg_delta
    symbol.curr_data[symbol.PRICE_DIFF] = price_diff
    symbol.curr_data[symbol.LAST_AVG_PRICE] = current_avg
    symbol.curr_data[symbol.CURRENT_PRICE] = current_price
    symbol.curr_data[symbol.LAST_VOL_TIMESTAMP] = timestamp
    symbol.curr_data[symbol.LAST_VOL] = curr_vol

    return [curr_quantity_delta, curr_qty, top_3_delta, old_cost_delta, cost_delta, avg_delta, current_price,
            price_diff]


def run():
    all_symbols_list = morning_routine.get_prepared_data()

    instrument_list_for_zerodha = []
    instrument_token_to_name_map = dict()

    for symbol in all_symbols_list:
        instrument_string = symbol.zerodha_info['exchange'] + ":" + symbol.zerodha_info['trading_symbol']
        instrument_list_for_zerodha.append(instrument_string)
        instrument_token_to_name_map[symbol.zerodha_info['instrument_token']] = symbol

    kite = zerodha.get_kiteconnect_instance()
    logger.info("Starting The Cyclic Application")
    while True:
        current_quotes = kite.quote(instrument_list_for_zerodha)
        for q in current_quotes:
            quote = current_quotes[q]
            symbol = instrument_token_to_name_map[quote['instrument_token']]
            curr_vol = quote["volume"]
            timestamp = quote["timestamp"]
            current_avg = quote["average_price"]

            check_update(symbol, curr_vol, current_avg, timestamp)
            print(symbol.name, symbol.curr_data[symbol.CURRENT_PRICE], current_avg)

        write(all_symbols_list)
        logger.info("Successfully written at {}".format(datetime.datetime.now()))
        time.sleep(60 * 6)


