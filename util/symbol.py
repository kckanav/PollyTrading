class Symbol:
    """
    This is the Symbol class
    """

    LOT_SIZE = "lot_size"
    TOP_3 = "top_3"
    OLD_OI = "old_oi"
    O_COST = "o_cost"
    COST = "cost"
    O_AVG = "o_avg"

    QTY = 'QTY'
    QTY_DELTA = 'D_QTY'
    TOP_3_DELTA = '% Top-3'
    O_COST_DELTA = '% O-Cost'
    COST_DELTA = '% Cost'
    AVG_DELTA = '% Avg'
    PRICE_DIFF = "Diff"

    TRADING_SYMBOL = "trading_symbol"
    INSTRUMENT_TOKEN = "instrument_token"
    EXCHANGE = "exchange"

    LAST_VOL = "last_vol"
    LAST_VOL_TIMESTAMP = "last_vol_timestamp"
    CURRENT_PRICE = "Current"
    LAST_AVG_PRICE = "average_price"
    NUMBER_OF_TICKS = "total_hits"

    def __init__(self, my_dict=None):

        self.name = None
        self.data = {
            self.LOT_SIZE: None, self.TOP_3: None, self.OLD_OI: None, self.O_COST: None, self.COST: None, self.O_AVG: None
        }

        self.zerodha_info = {
            self.TRADING_SYMBOL: None, self.INSTRUMENT_TOKEN: None, self.EXCHANGE: None,
        }

        self.curr_data = {
            self.LAST_VOL: 0, self.LAST_VOL_TIMESTAMP: None, self.CURRENT_PRICE: 0, self.LAST_AVG_PRICE: 0, self.NUMBER_OF_TICKS: 0
        }

        self.actionable = False

        if my_dict:
            for key in my_dict:
                setattr(self, key, my_dict[key])


    def __str__(self):
        return str({
            "name": self.name, "data": self.data, "zerodha_info": self.zerodha_info, "curr_data": self.curr_data, "actionable": self.actionable
        })

    def add_api_info(self, info):
        self.zerodha_info[self.TRADING_SYMBOL] = info[self.TRADING_SYMBOL]
        self.zerodha_info[self.INSTRUMENT_TOKEN] = info[self.INSTRUMENT_TOKEN]
        self.zerodha_info[self.EXCHANGE] = info[self.EXCHANGE]

    def gen_string_for_trade_xslx(self):
        data = self.data
        curr_data = self.curr_data

        if self.curr_data[self.LAST_VOL_TIMESTAMP] is None:
            return [data[self.OLD_OI],
                data[self.LOT_SIZE],
                data[self.TOP_3],
                data[self.O_COST],
                data[self.COST],
                data[self.O_AVG],
                self.name]

        return [curr_data[self.LAST_VOL_TIMESTAMP],
                data[self.OLD_OI],
                data[self.LOT_SIZE],
                data[self.TOP_3],
                data[self.O_COST],
                data[self.COST],
                data[self.O_AVG],
                self.name,
                curr_data[self.QTY_DELTA],
                curr_data[self.QTY],
                curr_data[self.TOP_3_DELTA],
                curr_data[self.O_COST_DELTA],
                curr_data[self.COST_DELTA],
                curr_data[self.AVG_DELTA],
                curr_data[self.LAST_AVG_PRICE],
                curr_data[self.PRICE_DIFF],
                "Yes" if self.actionable else ""]

