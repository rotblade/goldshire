import datetime
import numpy as np
from .helper import csv2df, get_lastprice


class Invest:
    '''
    Represent long term investment in one currency.
    '''
    def __init__(self, files, csvpath, currency):
        dfs = csv2df(files, csvpath)
        self._stocks = dfs[0]
        self._trades = dfs[1]
        self._divids = dfs[2]
        self.csvpath = csvpath
        self.currency = currency

    def __repr__(self):
        return (f'{slef.__class__.__name__} - {self.currency}')

    def _tidy_trades(self):
        '''
        Add actual money amount to trades dataframe.
        '''
        proceed = self._trades['Price'] * self._trades['Qty'].abs()
        fee = self._trades['Commission'] + self._trades['Tax']
        self._trades['Basis'] = np.where(self._trades['Transaction'] == 'BUY',
                                         proceed + fee, proceed - fee)

    def _tidy_dividends(self):
        '''
        Add actual income from dividend.
        '''
        fee = self._divids['Commission'] + self._divids['Tax']
        self._divids['Dividend'] = self._divids['PerShare'] * \
            self._divids['Qty'] - fee

    def _calc_tradedata(self):
        '''
        Claculate concerned trade data that includes:
            1. Total bought/sold qty.
            2. Weighted Average bought/sold price.
            3. Dividend income.
            4. Realized profit/loss.
            5. Unrealized profit/loss.
        '''
        group_trade = self._trades.groupby(
            [self._trades.index, self._trades['Transaction']])
        group_divid = self._divids.groupby(self._divids.index)

        # Claculate total bought/sold qty for each stock.
        qty_sum = group_trade['Qty'].sum().unstack(fill_value=0)
        df = self._stocks.join(qty_sum)
        df.columns = ['Name', 'Hold', 'B_Qty', 'S_Qty']
        df['Qty'] = df['B_Qty'] + df['S_Qty']

        # Calculate average bought/sold price.
        basis_sum = group_trade['Basis'].sum().unstack(fill_value=0)
        df['B_Cost'] = basis_sum['BUY'] / df['B_Qty']
        df['S_Cost'] = basis_sum['SELL'] / df['S_Qty'].abs()

        # Calculate dividend for each stock.
        df['Dividend'] = group_divid['Dividend'].sum()
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

    def setdata(self):
        self._tidy_trades()
        self._tidy_dividends()

        self.data = self._calc_tradedata()

    def get_summary(self, showAll=False):
        '''
        Get stocks summary.
        '''
        # Show only holding stocks by default
        stocks = self.data.loc[lambda df: df.Qty >
                               0] if not showAll else self.data
        # Extract useful summary fields.
        summary = stocks.reset_index()[['Symbol', 'Name', 'Currency',
                          'Qty', 'Last', 'Earning', 'Return']]

        return summary.round(2)


    def get_stock(self, symbol):
        '''
        Get detail for one traded stock.
        '''
        return self.data.loc[symbol]

    @staticmethod
    def whichMarket(symbol):
        if symbol.isdigit():
            if len(symbol) > 5:
                return 'CNY'
            else:
                return 'HKD'
        else:
            return 'USD'
