import datetime
import datetime as dt


API_KEY = "axvi4du8iyg02tbn"
API_SECRET = "iq3rqcmy0a41mhdm7wgacyz3u9l0jw6g"

DATA_DIRECTORY = "/Users/kanavgupta/Desktop/pollytrading/daily_prep/daily_files/"
HIST_SYMBOL_DATA_DICT_FILE = dt.date.today().isoformat() + "_hist_sym_data_dict.json"

CREDENTIALS_DIRECTORY = "/Users/kanavgupta/Desktop/pollytrading/api/daily_files/"
TODAY_CREDENTIALS_FILE = dt.date.today().isoformat() + "_today_credentials_list.json"

TODAY_LOG_FILE = DATA_DIRECTORY + dt.date.today().isoformat() + "_log_file.log"

USER_TOTAL_NUMBER_OF_SYMBOLS = 187


DATE_TIME_FORMAT = "Date: %a, %d %b %y %H:%M:%S"
LOG_TIME_DIFFERENCE = dt.timedelta(0, 10)
CALCULATION_TIME_DIFFERENCE = dt.timedelta(0, 180)
MIN_RATIO_VOL_TO_OI = 0.35

EXPIRY_DATE = datetime.date(2023, 10, 26)
EXPIRY_DATE_2 = EXPIRY_DATE - dt.timedelta(2, 0)

