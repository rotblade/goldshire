import datetime
import pandas as pd
import numpy as np
from os.path import join
from helper import get_tx_quotes, quotes2csvs


stocks_cny = pd.read_csv('csv/stocks-cny.csv', dtype={'Symbol': str, 'Hold': np.bool})
stocks_hkd = pd.read_csv('csv/stocks-hkd.csv', dtype={'Symbol': str, 'Hold': np.bool})
stocks_usd = pd.read_csv('csv/stocks-usd.csv', dtype={'Symbol': str, 'Hold': np.bool})

csvpath = '/Users/gavin/code/goldshire/goldshire/csv/historic'
today = datetime.date.today().strftime('%Y-%m-%d')

if __name__ == '__main__':
    hold_cny = stocks_cny.loc[lambda df: df.Hold]
    hold_hkd = stocks_hkd.loc[lambda df: df.Hold]
    hold_usd = stocks_usd.loc[lambda df: df.Hold]

    if len(hold_cny) > 0:
        quotes_cny = get_tx_quotes(hold_cny['Symbol'], market='cn')
        quotes2csvs(quotes_cny['Last'], today, csvpath)

    if len(hold_hkd) > 0:
        quotes_hkd = get_tx_quotes(hold_hkd['Symbol'], market='hk')
        quotes2csvs(quotes_hkd['Last'], today, csvpath)

    if len(hold_usd) > 0:
        quotes_usd = get_tx_quotes(hold_usd['Symbol'], market='us')
        quotes2csvs(quotes_usd['Last'], today, csvpath)
