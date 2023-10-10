import datetime
import datetime as dt
import os
import glob

IST_TZ = datetime.timezone(datetime.timedelta(hours = 5, minutes = 30), name="IST")
dt = datetime.datetime.now(tz = IST_TZ)
# ---------- FILE NAME CONSTANTS -----------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_FORMAT_FOR_FILENAME = dt.date().isoformat()


ZERODHA_DIR = ROOT_DIR + "/api/daily_files"
ZERODHA_LOG_FILE = ZERODHA_DIR + "/zer_log.log"
ZERODHA_CREDENTIALS_FILE = ZERODHA_DIR + "/zer_credentials.json"


HISTORY_DIR = ROOT_DIR + "/history/daily_files"
HISTORY_FILE_UPLOAD_DIRECTORY = HISTORY_DIR + "/historical_data/"


def latest_uploaded_file():
    files = glob.glob(HISTORY_FILE_UPLOAD_DIRECTORY + "/*")
    return max(files, key = os.path.getctime)


HISTORY_LOG_FILE = HISTORY_DIR + "/hist.log"
HISTORY_GENERATED_FILE = HISTORY_FILE_UPLOAD_DIRECTORY + "/" + DATE_FORMAT_FOR_FILENAME + "_list_extracted_from_xlsx.json"


RUNTIME_FILES = ROOT_DIR + "/run/daily_files"
RUNTIME_LOG_FILE = RUNTIME_FILES + "/run_log.log"
RUNTIME_GENERATED_FILE = RUNTIME_FILES + "/" + DATE_FORMAT_FOR_FILENAME + "_TRADE.csv"


def latest_runtime_trade_file():
    fi = glob.glob(RUNTIME_FILES + "/*.csv")
    return max(fi, key = os.path.getctime)

# RUNTIME_GENERATED_FILE = "hi.csv"
# --------------------------------------------


# -----------RUNTIME CONSTANTS ---------------
USER_TOTAL_NUMBER_OF_SYMBOLS = 186

TIME_INTERVAL = 60 * 6
D_QTY_PERCENTAGE_ALERT = 0.04

EXPIRY_DATE = datetime.date(2023, 10, 26)
EXPIRY_DATE_2 = EXPIRY_DATE - datetime.timedelta(days=2)

