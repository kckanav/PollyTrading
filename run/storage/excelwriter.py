import csv

import constants
from util.symbol import Symbol


def write_to_trade(symbols: [Symbol]):
    # field names
    fields = ['Timestamp', 'OLD OI', 'Lot', 'Top-3', 'O-Cost', 'Cost', 'O-Avg', 'Symbol', 'D.QTY', 'QTY', '% Top-3', '% O-Cost',
              '% Cost', '% Avg', 'Current', 'Diff', 'Actionable']

    rows = []
    for symbol in symbols:
        rows.append(symbol.gen_string_for_trade_xslx())

    # name of csv file
    filename = constants.RUNTIME_GENERATED_FILE

    # writing to csv file
    with open(filename, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(fields)

        # writing the data rows
        csvwriter.writerows(rows)
        csvwriter.writerow([])