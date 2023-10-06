from collections import defaultdict

import constants
from util.symbol import Symbol
import pandas as pd
import logging

DATA_XSLX_S_NO = "S.No"
DATA_XSLX_SYMBOL_NAME = "Symbol"
DATA_XSLX_COST = "Cost"
DATA_XSLX_OLD_OI = "OLD OI"
DATA_XSLX_LOT_SIZE = "Lot"
DATA_XSLX_O_COST = "O.Cost"
DATA_XSLX_AVG = "O-Avg"
DATA_XSLX_TOP_3 = "Top-3"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(constants.HISTORY_LOG_FILE)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_all_symbols(filename):
    f"""
    Extracts data from {filename} and creates all symbols present in {filename} with data populated
    in it that was present in the Excel File. Each symbol follows the {Symbol}. 

    The data populated here is old_oi, cost, o_cost, o_avg and lot_size.

    :param filename: DATA-$ where $ is the day of the month. 
    :return: A list of Symbols [{Symbol}]
    """
    df = pd.DataFrame(pd.read_excel(filename))

    sorted = df.sort_values(by = [DATA_XSLX_SYMBOL_NAME], ascending = [True])

    instruments = defaultdict(Symbol)

    count = 0
    # Iterate through the sorted DataFrame
    for index, row in sorted.iterrows():
        symbol_name = row[DATA_XSLX_SYMBOL_NAME]

        underlying_stock_name = symbol_name.split()[0]
        curr_symbol = instruments[underlying_stock_name]

        curr_symbol.data[curr_symbol.OLD_OI] = row[DATA_XSLX_OLD_OI]
        curr_symbol.data[curr_symbol.LOT_SIZE] = row[DATA_XSLX_LOT_SIZE]
        curr_symbol.data[curr_symbol.TOP_3] = row[DATA_XSLX_TOP_3]
        curr_symbol.data[curr_symbol.O_COST] = row[DATA_XSLX_O_COST]
        curr_symbol.data[curr_symbol.COST] = row[DATA_XSLX_COST]
        curr_symbol.data[curr_symbol.O_AVG] = row[DATA_XSLX_AVG]
        curr_symbol.name = underlying_stock_name

        count += 1

    if count != constants.USER_TOTAL_NUMBER_OF_SYMBOLS:
        logger.warning("Unexpected number of symbols. Expected: USER_TOTAL_NUMBER_OF_SYMBOLS = {}."
                       " Symbols added from file = {}".format(constants.USER_TOTAL_NUMBER_OF_SYMBOLS, count))
    else:
        logger.info("Created {} Symbol Objects from {}".format(len(instruments), filename))

    return [x for x in instruments.values()]
