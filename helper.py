import pandas as pd
import numpy as np
import requests
import csv
from os.path import join

def csv2df(csvs, csvpath):
    '''
    csvs[0]: CSV file that includes stocks info.
    csvs[1]: CSV file that includes trades info.
    csvs[2]: CSV file that includes dividend info.

    Return: A tuple with Pandas dataframe for the 3 CSV files.
    '''
    stocks = pd.read_csv(csvpath + csvs[0], dtype={'Symbol': str})
    trades = pd.read_csv(csvpath + csvs[1],
                         dtype={'Symbol': str, 'Qty': np.int64})
    divids = pd.read_csv(csvpath + csvs[2],
                         dtype={'Symbol': str, 'Qty': np.int64})

    # Set stock's symbol as Dataframe index.
    stocks.set_index('Symbol', inplace=True)
    trades.set_index('Symbol', inplace=True)
    divids.set_index('Symbol', inplace=True)

    return (stocks, trades, divids)


def quotes2csvs(symbols, datestring, csvpath):
    '''
    symbols: A pandas Series with index='stock code' & column='close price'.

    Output: Open corresponding historic csv file for each stock code. Then
    write today's close price into it.
    '''
    for k, v in symbols.items():
        # print((k, datestring, v))
        with open(join(csvpath, k+'.csv'), 'a', newline='') as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow([datestring, v])


def get_lastprice(symbols, csvpath):
    prices = []
    for symbol in symbols:
        df = pd.read_csv(join(csvpath, symbol+'.csv'))
        prices.append(df.iloc[-1, 1])

    return pd.Series(prices, index=symbols)

def get_tx_quotes(symbols, market='cny'):
    tx_api = 'http://qt.gtimg.cn/q=s_'
    if market=='cny':
        # codes = symbols.apply(lambda s: 'sz'+s if s[:2]=='00' else 'sh'+s)
        codes = ['sz'+s if s[:2]=='00' else 'sh'+s for s in symbols]
    else:
        if market=='hkd':
            # codes = 'hk' + symbols
            codes = ['hk'+s for s in symbols]
        else:
            # codes = 'us' + symbols
            codes = ['us'+s for s in symbols]

    # stocks_url = tx_api + codes
    urls = [tx_api+s for s in codes]
    lasts=[]
    for url in urls:
        r = requests.get(url)
        lasts.append(r.text.split('~')[3:6])

    cols = ['Last', 'Change', 'Percent']
    return pd.DataFrame(lasts, columns=cols, index=symbols)


def get_forexrate(s_currency, t_currency):
    av_api = 'https://www.alphavantage.co/query'
    params = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': s_currency,
        'to_currency': t_currency,
        'apikey': '24JJSPF9FOR8DS08'
    }

    r = requests.get(av_api, params=params)
    rate = r.json()['Realtime Currency Exchange Rate']['5. Exchange Rate']
    return float(rate)