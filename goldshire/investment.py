import datetime
import pandas as pd
from pandas.tseries.offsets import DateOffset
import numpy as np
from os.path import join
import config


class Invest:
    '''
    Represent long term investment in one base currency.
    '''

    def __init__(self, currency, fund, stocks, csvpath ):
        self.currency = currency
        self._stocks = stocks
        fund = pd.read_csv(csvpath+fund, parse_dates=['Date'], index_col=0)
        fund['Capital'] = fund['Amount'] * fund['Exchange']
        self._fund = fund
        self.initial = fund.iloc[0, 5]
        self.start = datetime.date(2016, 1, 1)


class Stocks:
    '''
    Represent a basket of stocks with their trade & dividend records.
    '''

    def __init__(self, currency, records, csvpath):
        self.currency = currency
        self._csvpath = csvpath

        trades = pd.read_csv(records[0], parse_dates=['Date'],
                             dtype={'Symbol': str, 'Qty': np.int64})
        trades.set_index('Symbol', inplace=True)

        proceed = trades['Price'] * trades['Qty'].abs()
        fee = trades['Commission'] + trades['Tax']
        trades['Basis'] = np.where(
            trades['Transaction'] == 'BUY', proceed + fee, proceed - fee)
        self._trades = trades

        dividends = csv2df(records[1]).set_index('Symbol')
        fee = dividends['Commission'] + dividends['Tax']
        dividends['Dividend'] = dividends['PerShare'] * dividends['Qty'] - fee
        self._dividends = dividends

    def getPrice(self, symbols, day=datetime.date.today()):
        prices = []
        for symbol in symbols:
            df = pd.read_csv(join(self._csvpath+'historic/', symbol + '.csv'),
                             names=['date', 'price'], parse_dates=['date']
                             index_col=0)
            if day not in df.index:
                day_range = pd.date_range(day-DateOffset(days=10),
                                          day-DateOffset(days=1))
                isFound = False
                for d in day_range:
                    if d in df.index:
                        day = d
                        isFound = True
                        break;
                if not isFound:
                    raise KeyError('No price found for specific date!')

            prices.append(df.loc[day, 'price'])

        return pd.Series(prices, index=symbols)


    def getHolding(self, end_date=datetime.date.today()):
        until = pd.Timestamp(end_date)

        trades = self._trades.loc[lambda df: df.Date <= until]
        dividends = self._dividends.loc[lambda df: df.Date <= until]

        grp_trade = trades.groupby([trades.index, trades['Transaction']])
        grp_dividend = dividends.groupby(dividends.index)

        stocks = trades[['Name']].drop_duplicates()
        bs_sum = grp_trade['Qty'].sum().unstack(fill_value=0)
        df = stocks.join(bs_sum)
        return df['Name'].loc[lambda df: df.BUY+df.SELL > 0]


    def getStocks(self, end_date=datetime.date.today()):
        until = pd.Timestamp(end_date)

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
        df['Last'] = self.getPrice(hold.index, str(end_date))
        df['UR_PnL'] = df['Qty'] * (df['Last'] - df['B_Cost'])
        df['UR_PnL'].fillna(0.0, inplace=True)

        # Calculate total earning for each stock.
        df['Earning'] = df['Dividend'] + df['R_PnL'] + df['UR_PnL']

        # Calculate return for each stock.
        df['Return'] = df['Earning'] / (df['B_Qty'] * df['B_Cost'])

        # Add currency info
        df['Currency'] = self.currency.capitalize()

        return df
