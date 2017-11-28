import datetime
import pandas as pd
import numpy as np


def csv2df(file):
    '''
    Convert a csv file to Pandas dataframe.
    '''
    return pd.read_csv(file, parse_dates=['Date'], dtype={'Symbol': str, 'Qty': np.int64})


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

    def __init__(self, currency, records):
        self.currency = currency

        trades = csv2df(records[0]).set_index('Symbol')
        proceed = trades['Price'] * trades['Qty'].abs()
        fee = trades['Commission'] + trades['Tax']
        trades['Basis'] = np.where(
            trades['Transaction'] == 'BUY', proceed + fee, proceed - fee)
        self._trades = trades

        dividends = csv2df(records[1]).set_index('Symbol')
        fee = dividends['Commission'] + dividends['Tax']
        dividends['Dividend'] = dividends['PerShare'] * dividends['Qty'] - fee
        self._dividends = dividends

    def getStocks(self, end_date=datetime.date.today()):
        until = pd.Timestamp(end_data)

        trades = self._trades.loc[lambda df: df.Date <= until]
        dividends = self._dividends.loc[lambda df: df.Date <= until]

        grp_trade = trades.groupby([trades.index, trades['Transaction']])
        grp_dividend = dividends.groupby(dividends.index)

        # Claculate total bought/sold qty for each stock.
        qty_sum = grp_trade['Qty'].sum().unstack(fill_value=0)
        #df = self._stocks.join(qty_sum)
        #df.columns = ['Name', 'Hold', 'B_Qty', 'S_Qty']
        #df['Qty'] = df['B_Qty'] + df['S_Qty']
