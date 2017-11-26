import datetime
import pandas as import pd
import numpy as np


def csv2df(file):
    '''
    Convert a csv file to Pandas dataframe.
    '''
    return pd.read_csv(file, dtype={'Symbol': str, 'Qty': np.int64})


class Invest:
    '''
    Represent long term investment in one base currency.
    '''
    def __init__(self, funds, stocks, currency):
        pass



class Stocks:
    '''
    Represent a basket of stocks with their trade & dividend records.
    '''
    def __init__(self, records, currency):
        self.currency = currency
        self._trades = csv2df(records[0]).set_index('Symbol')
        self._dividens = csv2df(records[1]).set_index('Symbol')
