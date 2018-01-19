# -*- coding: utf-8 -*-


import datetime
import pandas as pd
import numpy as np
from config import Config
from helper import getValidDay


class Portfolio:
    """
    Represent a basket of stocks in one currency, with their trade & dividend
    records.
    """
    def __init__(self, currency, records):
        """
        :param currency: `String` object that helds currency of Portfolio.
        :param records: `List` of `String` object that list trade & dividend
            csv filenames.
            records[0]: csv filename to store trade records.
            records[1]: csv filename to store dividend records.
        """
        self.currency = currency.upper()

        trade_file = Config.CSV_DIR/records[0]
        trades = pd.read_csv(trade_file, parse_dates=['Date'],
                             dtype={'Symbol': str, 'Qty': np.int64})
        trades.set_index('Symbol', inplace=True)
        proceed = trades['Price'] * trades['Qty'].abs()
        fee = trades['Commission'] + trades['Tax']
        trades['Cost'] = np.where(
            trades['Transaction'] == 'BUY', proceed + fee, proceed - fee
        )
        self._trades = trades

        dividend_file = Config.CSV_DIR/records[1]
        dividends = pd.read_csv(dividend_file, parse_dates=['Date'],
                                dtype={'Symbol': str, 'Qty': np.int64})
        dividends.set_index('Symbol', inplace=True)
        fee = dividends['Commission'] + dividends['Tax']
        dividends['Dividend'] = dividends['PerShare'] * dividends['Qty'] - fee
        self._dividends = dividends


    def __repr__(self):
        return (f'{self.__class__.__name__}-{self.currency}: \
                {len(self._trades)} trades & {len(self._dividends)} dividends')


    def _preCal(self, end):
        """
        Calculate interested portfolio info from raw trade data. For instance,
            'Qty': The quantity of currenty holding for one stock.
            'B_Cost': Average bought cost.
            'S_Cost': Average sold cost.

        :param end: `Date` object, the cut-off date to calculate.

        """
        until = pd.Timestamp(end)

        trades = self._trades.loc[lambda df: df.Date <= until]
        grp_trade = trades.groupby([trades.index, trades['Transaction']])
        stocks = trades[['Name']].drop_duplicates()
        bs_sum = grp_trade['Qty', 'Cost'].sum().unstack(fill_value=0)
        if len(bs_sum.columns) < 4:
            bs_sum.insert(1, 'S_Qty', 0)
            bs_sum.insert(3, 'S_Cost', 0.0)

        bs_sum.columns = ['B_Qty', 'S_Qty', 'B_Cost', 'S_Cost']
        df = stocks.join(bs_sum)
        df['Qty'] = df['B_Qty'] + df['S_Qty']
        df['B_Avg'] = df['B_Cost'] / df['B_Qty']
        df['S_Avg'] = df['S_Cost'] / df['S_Qty'].abs()
        df['S_Avg'].fillna(0.0, inplace=True)

        return df.round(3)


    def getHolding(self, end=datetime.date.today()):
        """
        Return stocks that were hold in specified date.

        :param day: `Date` object, the day to query holding stocks.
        """
        df = self._preCal(end)
        return df[['Name', 'Qty']].loc[lambda df: df.Qty > 0]


    def getPrice(self, end=datetime.date.today()):
        """
        Get close price for the holding stocks in specified date.

        :param day: `Date` object, the day to query price.
        """
        data = []
        symbols = self.getHolding(end).index
        rates = pd.read_csv(Config.H2C_RATE_FILE, parse_dates=['Date'],
                            index_col=0)

        for symbol in symbols:
            prices = pd.read_csv(Config.HISTORIC_DIR/f'{symbol}.csv',
                                 parse_dates=['Date'], index_col=0)
            #day = end
            #if day not in df.index:
            #    day_stamp = pd.Timestamp(day)
            #    if day_stamp > df.index[0]:
            #        day = df.loc[:day].index[-1]
            #    else:
            #        raise KeyError(f'No price found for {symbol} on {day}')
            price_day = getValidDay(prices, end)
            close = prices.loc[price_day, 'Close']
            # 如果境内人民币组合里有港股通股票，需要将其报价乘以汇率
            if self.currency == 'CNY':
                if len(symbol) == 5:
                    rate_day = getValidDay(rates, end)
                    close = close * rates.loc[rate_day, 'Rate']
            data.append(close)

        return pd.Series(data, index=symbols)


    def _calPnL(self, pre_df, end):
        """
        Calculate profit & loss for all traded stocks.

        :param pre_df: `DataFrame` object, returned by `_preCal` method.
        :param end: `Date` object, the up-to day to calculate.
        """
        until = pd.Timestamp(end)

        # Add Commission & Tax fields
        trades = self._trades.loc[lambda df: df.Date <= until]
        grp_trade = trades.groupby(trades.index)
        df = pre_df.join(grp_trade['Commission', 'Tax'].sum())

        # Calculate realized profit/loss
        basis = df['B_Avg'] * df['S_Qty'].abs()
        df['R_PnL'] = df['S_Cost'] - basis

        # Calcuate unrealized profit/loss
        hold = df.loc[lambda df: df.Qty > 0]
        df['Last'] = self.getPrice(end)
        df['UR_PnL'] = df['Qty'] * (df['Last'] - df['B_Avg'])
        df['UR_PnL'].fillna(0.0, inplace=True)

        return df.round(3)


    def _calDividend(self, end):
        """
        Calculate dividend for all traded stocks.

        :param end: `Date` object, the up-to day to calculate.
        """
        until = pd.Timestamp(end)

        dividends = self._dividends.loc[lambda df: df.Date <= until]
        grp_dividend = dividends.groupby(dividends.index)
        divids = grp_dividend['Commission', 'Tax', 'Dividend'].sum()

        return divids.round(3)


    def getStocks(self, end=datetime.date.today()):
        """
        Return overall performance for each traded stock.

        :param end: `Date` object, the up-to day to calculate.
        """
        pre_df = self._preCal(end)
        df = self._calPnL(pre_df, end)
        df = df.join(self._calDividend(end), lsuffix='_t', rsuffix='_d')
        df['Commission_d'].fillna(0.0, inplace=True)
        df['Tax_d'].fillna(0.0, inplace=True)
        df['Dividend'].fillna(0.0, inplace=True)
        df['Commission'] = df['Commission_t'] + df['Commission_d']
        df['Tax'] = df['Tax_t'] + df['Tax_d']

        # Calculate total earning for each stock.
        df['Earning'] = df['Dividend'] + df['R_PnL'] + df['UR_PnL']

        # Calculate return for each stock.
        df['Return'] = df['Earning'] / df['B_Cost']

        # Calculate market value for holding stocks.
        df['Value'] = df['Last'] * df['Qty']

        columns = [
            'Name', 'Qty', 'B_Cost', 'Commission', 'Tax', 'Last', 'R_PnL',
            'UR_PnL', 'Dividend', 'Value', 'Earning', 'Return',
        ]

        return df[columns].round(3)
