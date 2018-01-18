import datetime
import pandas as pd
import numpy as np
import requests
import csv
from os.path import join
from config import Config

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


def record2file(filepath, record, day=datetime.date.today()):
    df = pd.read_csv(filepath, names=['Date', 'Close'],
                     parse_dates=['Date'], index_col=0)
    pd_day = pd.Timestamp(day)
    if pd_day > df.index[-1]:
        df.loc[pd_day] = record
        df.to_csv(filepath)


def get_lastprice(symbols, csvpath):
    prices = []
    for symbol in symbols:
        df = pd.read_csv(join(csvpath, symbol+'.csv'))
        prices.append(df.iloc[-1, 1])

    return pd.Series(prices, index=symbols)

def get_tx_quotes(symbols):
    tx_api = Config.TENCENT_QUOTE_URL
    codes = []
    for s in symbols:
        if s.isdigit():
            if len(s) == 6:
                codes.append('sz'+s if s[:2]=='00' else 'sh'+s)
            else:
                # HKD market
                codes.append('hk'+s)
        else:
            # USD market
            codes.append('us'+s)

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
