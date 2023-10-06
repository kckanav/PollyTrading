import datetime
import datetime as dt
import os
import glob

IST_TZ = datetime.timezone(datetime.timedelta(hours = 5, minutes = 30), name="IST")
dt = datetime.datetime.now(tz = IST_TZ)
# ---------- FILE NAME CONSTANTS -----------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_FORMAT_FOR_FILENAME = dt.date().isoformat()

ZERODHA_FILES = ROOT_DIR + "/api/daily_files/" + DATE_FORMAT_FOR_FILENAME
ZERODHA_LOG_FILE = ZERODHA_FILES + "_zer_log.log"
ZERODHA_CREDENTIALS_FILE = ZERODHA_FILES + "_zer_credentials.json"

MORRNING_PREP_FILES = ROOT_DIR + "/daily_prep/daily_files/" + DATE_FORMAT_FOR_FILENAME
MORNING_PREP_LOG_FILE = MORRNING_PREP_FILES + "_morning_prep_log.log"
MORNING_PREP_DATA_FILE = MORRNING_PREP_FILES + "_morning_prep_data_list.json"

HISTORY_FILES = ROOT_DIR + "/history/daily_files/" + DATE_FORMAT_FOR_FILENAME
files = glob.glob(ROOT_DIR + "/history/daily_files/historical_data/*")
HISTORY_FILE_UPLOAD_DIRECTORY = ROOT_DIR +  "/history/daily_files/historical_data/"
HISTORY_USER_UPLOADED_FILE = max(files, key=os.path.getctime)
HISTORY_LOG_FILE = HISTORY_FILES + "_hist_log.log"
HISTORY_GENERATED_FILE = HISTORY_FILES + "_list_extracted_from_xlsx.json"

RUNTIME_FILES = ROOT_DIR + "/run/daily_files/" + DATE_FORMAT_FOR_FILENAME
RUNTIME_LOG_FILE = RUNTIME_FILES + "_run_log.log"
RUNTIME_GENERATED_FILE = RUNTIME_FILES + "_TRADE.csv"
# --------------------------------------------


# -----------RUNTIME CONSTANTS ---------------
USER_TOTAL_NUMBER_OF_SYMBOLS = 186

TIME_INTERVAL = 60 * 6
D_QTY_PERCENTAGE_ALERT = 0.04

EXPIRY_DATE = datetime.date(2023, 10, 26)
EXPIRY_DATE_2 = EXPIRY_DATE - datetime.timedelta(days=2)

