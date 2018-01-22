import datetime
import pandas as pd
import numpy as np
import requests
from os.path import join
from config import Config


def record2file(filepath, record, day=datetime.date.today()):
    df = pd.read_csv(filepath, parse_dates=['Date'], index_col=0)
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
    tx_api = Config.TENCENT_URL
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


def get_forexrate(api_url, params):
    r_json = requests.get(api_url, params=params).json()
    if r_json['success']:
        return r_json['quotes']
    else:
        return r_json['error']['coce']
