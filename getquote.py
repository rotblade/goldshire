import datetime
import pandas as pd
import numpy as np
import tushare as ts


def get_symbols(filename):
    stocks = pd.read_csv(filename, dtype={'Symbol': str, 'Hold': np.bool})
    return stocks.loc[lambda df: df.Hold]['Symbol']


def get_ts_quote(symbols, isA=True):
    cons = ts.get_apis()
    last = datetime.datetime.today() - datetime.timedelta(days=7)

    quotes_dict = {}
    for item in symbols:
        if isA:
            df = ts.bar(item, conn=cons, freq='D',
                        start_date=last, end_date='')
        else:
            df = ts.bar(item, conn=cons, asset='X',
                        start_date=last, end_date='')
        quotes_dict[item] = df['close'].iloc[0]

    quotes = pd.Series(quotes_dict)
    return quotes


if __name__ == '__main__':
    symbols = get_symbols('csv/stocks-cny.csv')
    quotes = get_ts_quote(symbols)
    print(quotes)
