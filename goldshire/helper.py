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
        codes = symbols.apply(lambda s: 'sz'+s if s[:2]=='00' else 'sh'+s)
    else:
        if market=='hkd':
            codes = 'hk' + symbols
        else:
            codes = 'us' + symbols

    stocks_url = tx_api + codes
    lasts=[]
    for k, v in stocks_url.items():
        r = requests.get(v)
        lasts.append(r.text.split('~')[2:6])

    cols = ['Symbol', 'Last', 'Change', 'Percent']
    return pd.DataFrame(lasts, columns=cols).set_index('Symbol')
