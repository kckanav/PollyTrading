import constants
from api import zerodha


def update(symbol, quote, quantity_delta_perc):
    curr_vol = quote[zerodha.ZER_VOLUME]
    timestamp = quote[zerodha.ZER_TIMESTAMP]
    current_avg = quote[zerodha.ZER_AVG_PRICE]
    message_list = []

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

    if symbol.curr_data[symbol.LAST_VOL] != 0 and curr_quantity_delta >= quantity_delta_perc:
        symbol.actionable = True
        symbol.curr_data[symbol.NUMBER_OF_TICKS] += 1
        message_list.append(symbol)
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

    return message_list
