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

        stocks = trades[['Name']].drop_duplicates()

        # Claculate total bought/sold qty for each stock.
        bs_sum = grp_trade['Qty'].sum().unstack(fill_value=0)
        df = stocks.join(bs_sum)
        df.columns = ['Name', 'B_Qty', 'S_Qty']
        df['Qty'] = df['B_Qty'] + df['S_Qty']

        # Calculate average bought/sold price.
        basis_sum = grp_trade['Basis'].sum().unstack(fill_value=0)
        df['B_Cost'] = basis_sum['BUY'] / df['B_Qty']
        df['S_Cost'] = basis_sum['SELL'] / df['S_Qty'].abs()

        # Calculate dividend for each stock.
        df['Dividend'] = grp_dividend['Dividend'].sum()
        df['Dividend'].fillna(0.0, inplace=True)

        # Calculate realized profit/loss
        sold_cost = df['B_Cost'] * df['S_Qty'].abs()
        df['R_PnL'] = basis_sum['SELL'] - sold_cost
        df['R_PnL'].fillna(0.0, inplace=True)

        # Calcuate unrealized profit/loss
        hold = df.loc[lambda df: df.Qty > 0]
        df['Last'] = get_lastprice(hold.index, self.csvpath+'history/')
        df['UR_PnL'] = df['Qty'] * (df['Last'] - df['B_Cost'])
        df['UR_PnL'].fillna(0.0, inplace=True)

        # Calculate total earning for each stock.
        df['Earning'] = df['Dividend'] + df['R_PnL'] + df['UR_PnL']

        # Calculate return for each stock.
        df['Return'] = df['Earning'] / (df['B_Qty'] * df['B_Cost'])


        # Add currency info
        df['Currency'] = self.currency

        return df
