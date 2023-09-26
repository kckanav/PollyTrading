from api import zerodha
from history import history
from daily_prep import morning_routine
from run import run
import logging

logger = logging.getLogger()

file_handler = logging.FileHandler('main.log')
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

if __name__ == '__main__':
    run.run()
