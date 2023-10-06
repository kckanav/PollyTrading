import sys

import constants
from run import run
import logging


logger = logging.getLogger()

file_handler = logging.FileHandler('main.log')
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

#logger.addHandler(file_handler)
logger.addHandler(stream_handler)

if __name__ == '__main__':
    # zerodha.login_with_terminal()
    try:
        d_qty = float(sys.argv[1]) / 100
        time_interval = float(sys.argv[2]) * 60
    except Exception as e:
        d_qty = constants.D_QTY_PERCENTAGE_ALERT
        time_interval = constants.TIME_INTERVAL

    run.run(time_delay = time_interval, quantity_delta_perc = d_qty)

