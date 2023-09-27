import json
from util.symbol import Symbol
from daily_prep import constants
import pandas as pd
from collections import defaultdict
import csv
import xlsxwriter
import logging


WRITE_FILE_NAME = "/home/ubuntu/pollytrading/history/daily_files/generated_history/" + constants.HIST_SYMBOL_DATA_DICT_FILE
READ_FILE_NAME = "/home/ubuntu/pollytrading/history/daily_files/historical_data/" + "DATA-22.xlsx"

TRADE_FILE_MARKER = 1
DATA_FILE_MARKER = 2
STOCK_FILE_MARKER = 3

TRADE_XSLX_S_NO = "S.No"
TRADE_XSLX_SYMBOL_NAME = "Symbol"
TRADE_XSLX_COST = "Cost"
TRADE_XSLX_OLD_OI = "OLD OI"
TRADE_XSLX_LOT_SIZE = "Lot"
TRADE_XSLX_O_COST = "O.Cost"
TRADE_XSLX_AVG = "O-Avg"
TRADE_XSLX_TOP_3 = "Top-3"

DATA_XSLX_S_NO = "S.No"
DATA_XSLX_SYMBOL_NAME = "Symbol"
DATA_XSLX_COST = "Cost"
DATA_XSLX_OLD_OI = "OLD OI"
DATA_XSLX_LOT_SIZE = "Lot"
DATA_XSLX_O_COST = "O.Cost"
DATA_XSLX_AVG = "O-Avg"
DATA_XSLX_TOP_3 = "Top-3"

STOCK_XSLX_SYMBOL_NAME = "SYMBOL"
STOCK_XSLX_DATE = "Date"
STOCK_XSLX_COST = "Cost"
STOCK_XSLX_OLD_OI = "OI"
STOCK_XSLX_LOT_SIZE = "Lot"
STOCK_XSLX_AVG = "Avg"

QTY = 'QTY'
QTY_DELTA = 'D_QTY'
TOP_3_DELTA = '% Top-3'
O_COST_DELTA = '% O-Cost'
COST_DELTA = '% Cost'
AVG_DELTA = '% Avg'
CURRENT_PRICE = "Current"
PRICE_DIFF = "Diff"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_all_symbols(file_name = WRITE_FILE_NAME):
    """
    Loads all symbols from {CONSTANTS.HIST_SYMBOL_DATA_DICT_FILE} which is list of Symbol
    :return: A list of Symbol objects. [Symbol, Symbol, ...]
    """
    try:
        with open(file_name, 'r') as f:
            all_symbols_json = json.load(f)
            all_symbols_list = []
            for symbol in all_symbols_json:
                symbol = Symbol(my_dict = symbol)
                all_symbols_list.append(symbol)

    # TODO: Handle other errors as well, like
    except FileNotFoundError:
        all_symbols_list = save_and_return_history(out_file = file_name)

    if len(all_symbols_list) != constants.USER_TOTAL_NUMBER_OF_SYMBOLS:
        logger.warning(
            "Number of Symbols MISMATCH: Loaded Symbol Objects = {} from {} | Expected = {} ".format(len(all_symbols_list),
                                                                                              file_name,
                                                                                              constants.USER_TOTAL_NUMBER_OF_SYMBOLS))
    else:
        logger.info("Created {} Symbol Objects from {}".format(len(all_symbols_list), file_name))

    return all_symbols_list


def save_and_return_history(in_file=READ_FILE_NAME, marker=DATA_FILE_MARKER, out_file=WRITE_FILE_NAME):
    """
    TODO :- Compute the marker based on the name of the in_file. Eg:- if it contains TRADE, marker is Trade instead
            explicitly asking for a marker as a parameter.

    Extracts data from an excel file which has historical data, creates Symbol object for each individual stock, and
    returns a List of Symbols

    :param in_file: The excel file from which to read data
    :param marker: Marker to indicate which kind of input file it is. (TRADE-$, STOCK-$, or DATA-$)
    :param out_file: The output json file to create, which will contain list of Symbol objects
    :return: List of Symbol objects with historical data filled in
    """
    if marker == TRADE_FILE_MARKER:
        symbols = return_history_from_trade_xslx(in_file)
    elif marker == DATA_FILE_MARKER:
        symbols = return_history_from_data_xslx(in_file)
    elif marker == STOCK_FILE_MARKER:
        symbols = return_history_from_stock_xslx(in_file)
    else:
        logger.critical("Invalid File Marker Entered for {}. Needs to be history.$_FILE_MARKER".format(in_file))
        return IndexError

    file_name = out_file
    with open(file_name, 'w') as f:
        json.dump(symbols, f, default = vars)
        logger.info("List of Symbol with only historical data created at {}".format(out_file))
    return symbols


def return_history_from_data_xslx(filename):
    f"""
    Extracts data from {filename} and creates all symbols present in {filename} with data populated
    in it. Each symbol follows the {Symbol}. 

    The data populated here is old_oi, cost, o_cost, o_avg and lot_size.

    :param filename: STOCK-$ where $ is the day of the month. 
    :return: A Dictionary of symbols, where keys are the SYMBOL NAME of the stock, and value is a {Symbol}

             Eg :- [AARTIIND: {Symbol}, "ABBOT": {Symbol}, ...]
    """
    df = pd.DataFrame(pd.read_excel(filename))

    sorted = df.sort_values(by = [DATA_XSLX_SYMBOL_NAME], ascending = [True])

    # Create a defaultdict called 'instruments' with a default value provided by the 'default_val' function
    instruments = defaultdict(Symbol)

    count = 0
    # Iterate through the sorted DataFrame
    for index, row in sorted.iterrows():
        symbol_name = row[DATA_XSLX_SYMBOL_NAME]

        underlying_stock_name = symbol_name.split()[0]
        curr_symbol = instruments[underlying_stock_name]

        curr_symbol.data['old_oi'] = row[DATA_XSLX_OLD_OI]
        curr_symbol.data['lot_size'] = row[DATA_XSLX_LOT_SIZE]
        curr_symbol.data['top_3'] = row[DATA_XSLX_TOP_3]
        curr_symbol.data['o_cost'] = row[DATA_XSLX_O_COST]
        curr_symbol.data['cost'] = row[DATA_XSLX_COST]
        curr_symbol.data['o_avg'] = row[DATA_XSLX_AVG]
        curr_symbol.name = underlying_stock_name

        count += 1

    if count != constants.USER_TOTAL_NUMBER_OF_SYMBOLS:
        logger.warning("Unexpected number of symbols. Expected: USER_TOTAL_NUMBER_OF_SYMBOLS = {}."
                       " Symbols added from file = {}".format(constants.USER_TOTAL_NUMBER_OF_SYMBOLS, count))

    logger.info("Historical Data Excel read for {} symbols from {} ".format(count, filename))
    return [x for x in instruments.values()]


def return_history_from_stock_xslx(filename):
    f"""
    Extracts data from {filename} and creates all symbols present in {filename} with data populated
    in it. Each symbol follows the {Symbol}. 

    The data populated here is old_oi, cost, o_cost, o_avg and lot_size.

    :param filename: STOCK-$ where $ is the day of the month. 
    :return: A Dictionary of symbols, where keys are the SYMBOL NAME of the stock, and value is a {Symbol}

             Eg :- [AARTIIND: {Symbol}, "ABBOT": {Symbol}, ...]
    """
    df = pd.DataFrame(pd.read_excel(filename))

    # Sort the DataFrame based on two columns, 'Date' in descending order and 'SYMBOL' in ascending order
    sorted = df.sort_values(by = [STOCK_XSLX_DATE, STOCK_XSLX_SYMBOL_NAME], ascending = [False, True])

    # Create a defaultdict called 'instruments' with a default value provided by the 'default_val' function
    instruments = defaultdict(Symbol)

    count = 0
    # Iterate through the sorted DataFrame
    for index, row in sorted.iterrows():
        symbol = row[STOCK_XSLX_SYMBOL_NAME]
        curr_symbol = instruments[symbol]
        # Check if 'cost' in the current symbol is empty (Means we are in the latest date table)
        if not curr_symbol.data['cost']:
            curr_symbol.name = row[STOCK_XSLX_SYMBOL_NAME]
            curr_symbol.data['lot_size'] = row[STOCK_XSLX_LOT_SIZE]
            curr_symbol.data['cost'] = row[STOCK_XSLX_COST]
            curr_symbol.data['o_avg'] = row[STOCK_XSLX_AVG]
            curr_symbol.data['old_oi'] = row[STOCK_XSLX_OLD_OI]

        # Check if 'o_cost' in the current symbol is empty (Means we are in the second latest table)
        elif not curr_symbol.data['o_cost']:
            curr_symbol.data['o_cost'] = row[STOCK_XSLX_COST]

        # If both 'cost' and 'o_cost', we have traversed neccesary data.
        else:
            break

        count += 1

    if count != constants.USER_TOTAL_NUMBER_OF_SYMBOLS:
        logger.warning("Unexpected number of symbols. Expected: USER_TOTAL_NUMBER_OF_SYMBOLS = {}."
                       " Symbols added from file = {}".format(constants.USER_TOTAL_NUMBER_OF_SYMBOLS, count))
    logger.info("Historical data loaded for {} symbols from {} ".format(count, filename))
    return [x for x in instruments.values()]


def return_history_from_trade_xslx(filename):
    f"""
    Extracts data from {filename} and creates all symbols present in {filename} with data populated
    in it. Each symbol follows the {Symbol}. 

    The data populated here is old_oi, cost, o_cost, o_avg and lot_size.

    :param filename: STOCK-$ where $ is the day of the month. 
    :return: A Dictionary of symbols, where keys are the SYMBOL NAME of the stock, and value is a {Symbol}

             Eg :- [AARTIIND: {Symbol}, "ABBOT": {Symbol}, ...]
    """
    df = pd.DataFrame(pd.read_excel(filename))

    sorted = df.sort_values(by = [TRADE_XSLX_S_NO], ascending = [True])

    # Create a defaultdict called 'instruments' with a default value provided by the 'default_val' function
    instruments = defaultdict(Symbol)

    count = 0
    # Iterate through the sorted DataFrame
    for index, row in sorted.iterrows():
        symbol_name = row[TRADE_XSLX_SYMBOL_NAME]

        if not isinstance(symbol_name, str):
            break

        underlying_stock_name = symbol_name.split()[0]
        curr_symbol = instruments[underlying_stock_name]

        # Check if 'cost' in the current symbol is empty (Means we are in the latest date table)
        if not curr_symbol.data['cost']:
            curr_symbol.data['old_oi'] = row[TRADE_XSLX_OLD_OI]
            curr_symbol.data['lot_size'] = row[TRADE_XSLX_LOT_SIZE]
            curr_symbol.data['top_3'] = row[TRADE_XSLX_TOP_3]
            curr_symbol.data['o_cost'] = row[TRADE_XSLX_O_COST]
            curr_symbol.data['cost'] = row[TRADE_XSLX_COST]
            curr_symbol.data['o_avg'] = row[TRADE_XSLX_AVG]
            curr_symbol.name = underlying_stock_name

        # If both 'cost' and 'o_cost', we have traversed neccesary data.
        else:
            break

        count += 1

    if count != constants.USER_TOTAL_NUMBER_OF_SYMBOLS:
        logger.warning(
            "Unexpected number of symbols. Expected: USER_TOTAL_NUMBER_OF_SYMBOLS = {}. Symbols added from file = {}".format(
                constants.USER_TOTAL_NUMBER_OF_SYMBOLS, count))

    logger.info("Historical data loaded for {} symbols from {} ".format(count, filename))
    return [x for x in instruments.values()]


def write(symbols: [Symbol]):
    # field names
    fields = ['OLD OI', 'Lot', 'Top-3', 'O-Cost', 'Cost', 'O-Avg', 'Symbol', 'D.QTY', 'QTY', '% Top-3', '% O-Cost',
              '% Cost', '% Avg', 'Current', 'Diff']

    rows = []
    for symbol in symbols:
        rows.append(symbol.gen_string_for_trade_xslx())

    # name of csv file
    filename = "first_trade_file.csv"

    # writing to csv file
    with open(filename, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(fields)

        # writing the data rows
        csvwriter.writerows(rows)
        csvwriter.writerow([])


def write_2(symbols):
    workbook = xlsxwriter.Workbook('Example2.xlsx')
    worksheet = workbook.add_worksheet()

    # Start from the first cell.
    # Rows and columns are zero indexed.
    row = 0
    column = 0

    fields = ['OLD OI', 'Lot', 'Top-3', 'O-Cost', 'Cost', 'O-Avg', 'Symbol', 'D.QTY', 'QTY', '% Top-3', '% O-Cost',
              '% Cost', '% Avg', 'Current', 'Diff']

    all_format = workbook.add_format({"num_format": "#,##0_ ;-#,##0", "align": "center"})
    derived = workbook.add_format({"num_format": "#,##0_ ;-#,##0", 'bg_color': 'yellow', "align": "center"})

    actionable_format = workbook.add_format({'bg_color': 'yellow', "align": "center"})

    header = workbook.add_format({})
    # iterating through content list
    for item in fields:
        # write operation perform
        worksheet.write(row, column, item)

        # incrementing the value of row by one
        # with each iterations.
        column += 1

    row = 1
    for symbol in symbols:
        li = symbol.gen_string_for_trade_xslx()
        column = 0
        for item in li:
            curr_format = all_format
            if column in range(7, 15):
                curr_format = derived
            worksheet.write(row, column, item, curr_format)
            column += 1
        if symbol.actionable:
            worksheet.write(row, column, 1, actionable_format)
        row += 1

    worksheet.set_column(7, 14, cell_format = derived)
    workbook.close()


if __name__ == '__main__':
    file_handler = logging.FileHandler('zerodha.log')
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    save_and_return_history()
