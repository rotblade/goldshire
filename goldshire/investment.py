import datetime
import numpy as np
import pandas as pd
from os.path import join
from forex_python.converter import CurrencyRates
# from .config import csvpath


class Invest:
    '''
    Represent long term investment in one base currency.
    '''

    def __init__(self, name, currency, fund, stocks, start=datetime.date(2016, 1, 1)):
        self.name = name
        self.currency = currency.upper()
        self.start = start
        fund = pd.read_csv(fund, parse_dates=['Date'], index_col=0)
        #c = CurrencyRates()

        #def c2BCurrency(r):
        #    if r.Currency.upper() == self.currency:
        #        return r.Amount
        #    else:
        #        return r.Amount * c.get_rate(r.Currency.upper(),
        #                                     self.currency, start)
        #fund['BaseAmount'] = fund.apply(c2BCurrency, axis=1)
        fund['BaseAmount'] = fund['Amount'] * fund['ExchangeRate']
        self._fund = fund
        self._stocks = stocks
        self.initial = fund.loc[:start]['BaseAmount'].sum()

    def __repr__(self):
        return (f'{self.__class__.__name__} - {self.currency}: {self.initial}')

    def getInvest(self, end=datetime.date.today()):
        fund = self._fund.loc[:end]['BaseAmount'].sum()
        invest = {
            #'name': self.name,
            #'currency': self.currency,
            'fund': fund,
            'position': 0.0,
            'earning': 0.0,
            'commission': 0.0,
            'tax': 0.0,
        }

        for s in self._stocks:
            df = s.getStocks(end)
            hold = df.loc[lambda df: df.Qty > 0]
            position = 0.0 if hold.empty else (hold['Last'] * hold['Qty']).sum()
            earning = df['Earning'].sum()
            commission = df['Commission_t'].sum() + df['Commission_d'].sum()
            tax = df['Tax_t'].sum() + df['Tax_d'].sum()

            if s.currency != self.currency:
                c = CurrencyRates()
                ex_rate = c.get_rate(s.currency, self.currency, end)
                position = position * ex_rate
                earning = earning * ex_rate
                commission = commission * ex_rate
                tax = tax * ex_rate

            invest['position'] += position
            invest['earning'] += earning
            invest['commission'] += commission
            invest['tax'] += tax

        invest['value'] = invest['fund'] + invest['earning']

        return invest


class Stocks:
    '''
    Represent a basket of stocks with their trade & dividend records.
    '''

    def __init__(self, currency, records):
        self.currency = currency.upper()

        trades = pd.read_csv(records[0], parse_dates=['Date'],
                             dtype={'Symbol': str, 'Qty': np.int64})
        trades.set_index('Symbol', inplace=True)

        proceed = trades['Price'] * trades['Qty'].abs()
        fee = trades['Commission'] + trades['Tax']
        trades['Basis'] = np.where(
            trades['Transaction'] == 'BUY', proceed + fee, proceed - fee)
        self._trades = trades

        dividends = pd.read_csv(records[1], parse_dates=['Date'],
                                dtype={'Symbol': str, 'Qty': np.int64})
        dividends.set_index('Symbol', inplace=True)
        fee = dividends['Commission'] + dividends['Tax']
        dividends['Dividend'] = dividends['PerShare'] * dividends['Qty'] - fee
        self._dividends = dividends


    def __repr__(self):
        return (f'{self.__class__.__name__}-{self.currency}: {len(self._trades)} trades & {len(self._dividends)} dividends')


    @staticmethod
    def getPrice(csvpath, symbols, day=datetime.date.today()):
        prices = []
        for symbol in symbols:
            df = pd.read_csv(join(csvpath + 'historic', symbol + '.csv'),
                             names=['date', 'price'], parse_dates=['date'],
                             index_col=0)
            if day not in df.index:
                day_stamp = pd.Timestamp(day)
                if day_stamp > df.index[0]:
                    day = df.loc[:day].index[-1]
                else:
                    raise KeyError(f'No price found for {symbol} on {day}')

            prices.append(df.loc[day, 'price'])

        return pd.Series(prices, index=symbols)


    def _preCal(self, end):
        until = pd.Timestamp(end)

        trades = self._trades.loc[lambda df: df.Date <= until]
        dividends = self._dividends.loc[lambda df: df.Date <= until]
        grp_trade = trades.groupby([trades.index, trades['Transaction']])
        stocks = trades[['Name']].drop_duplicates()
        bs_sum = grp_trade['Qty', 'Basis'].sum().unstack(fill_value=0)
        bs_sum.columns = ['B_Qty', 'S_Qty', 'B_Basis', 'S_Basis']
        df = stocks.join(bs_sum)
        df['Qty'] = df['B_Qty'] + df['S_Qty']
        df['B_Cost'] = df['B_Basis'] / df['B_Qty']
        df['S_Cost'] = df['S_Basis'] / df['S_Qty'].abs()

        return df


    def _getTrade(self, df, end):
        until = pd.Timestamp(end)

        # Add Commission & Tax fields
        trades = self._trades.loc[lambda df: df.Date <= until]
        grp_trade = trades.groupby(trades.index)
        df = df.join(grp_trade['Commission', 'Tax'].sum())

        # Calculate realized profit/loss
        sold_cost = df['B_Cost'] * df['S_Qty'].abs()
        df['R_PnL'] = df['S_Basis'] - sold_cost
        df['R_PnL'].fillna(0.0, inplace=True)

        # Calcuate unrealized profit/loss
        hold = df.loc[lambda df: df.Qty > 0]
        df['Last'] = Stocks.getPrice('csv/', hold.index, end)
        df['UR_PnL'] = df['Qty'] * (df['Last'] - df['B_Cost'])
        df['UR_PnL'].fillna(0.0, inplace=True)

        return df


    def _getDividend(self, end):
        until = pd.Timestamp(end)

        dividends = self._dividends.loc[lambda df: df.Date <= until]
        grp_dividend = dividends.groupby(dividends.index)
        divids = grp_dividend['Commission', 'Tax', 'Dividend'].sum()

        return divids


    def getHolding(self, end=datetime.date.today()):
        df = self._preCal(end)
        return df[['Name', 'Qty']].loc[lambda df: df.Qty > 0]


    def getStocks(self, end=datetime.date.today()):
        s_df = self._preCal(end)
        df = self._getTrade(s_df, end)
        df = df.join(self._getDividend(end), lsuffix='_t', rsuffix='_d')
        df['Commission_d'].fillna(0.0, inplace=True)
        df['Tax_d'].fillna(0.0, inplace=True)
        df['Dividend'].fillna(0.0, inplace=True)

        # Calculate total earning for each stock.
        df['Earning'] = df['Dividend'] + df['R_PnL'] + df['UR_PnL']

        # Calculate return for each stock.
        df['Return'] = df['Earning'] / (df['B_Qty'] * df['B_Cost'])

        # Add currency info
        df['Currency'] = self.currency.upper()

        return df
