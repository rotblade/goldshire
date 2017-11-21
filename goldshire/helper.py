import pandas as pd
import numpy as np
import requests

def csv2df(csvs):
    '''
    csvs[0]: CSV file that includes stocks info.
    csvs[1]: CSV file that includes trades info.
    csvs[2]: CSV file that includes dividend info.

    Return: A tuple with Pandas dataframe for the 3 CSV files.
    '''
    stocks = pd.read_csv('csv/' + csvs[0], dtype={'Symbol': str})
    trades = pd.read_csv('csv/' + csvs[1],
                         dtype={'Symbol': str, 'Qty': np.int64})
    divids = pd.read_csv('csv/' + csvs[2],
                         dtype={'Symbol': str, 'Qty': np.int64})

    return (stocks, trades, divids)


def get_tx_quotes(symbols, market='cn'):
    tx_api = 'http://qt.gtimg.cn/q=s_'
    if market=='cn':
        codes = symbols.apply(lambda s: 'sz'+s if s[:2]=='00' else 'sh'+s)
    else:
        if market=='hk':
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
