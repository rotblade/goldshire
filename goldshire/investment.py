import datetime
import numpy as np
import pandas as pd
from os.path import join
from pandas.tseries.offsets import DateOffset
from forex_python.converter import CurrencyRates
from config import csvpath


class Invest:
    '''
    Represent long term investment in one base currency.
    '''

    def __init__(self, currency, fund, stocks, start=datetime.date(2016,1,1)):
        self.currency = currency.upper()
        self.start = start
        fund = pd.read_csv(csvpath+fund, parse_dates=['Date'], index_col=0)
        c = CurrencyRates()
        def c2BCurrency(r):
            if r.Currency.upper() == self.currency:
                return r.Amount
            else:
                return r.Amount * c.get_rate(r.Currency.upper(),
                                             self.currency, start)
        fund['BaseAmount'] = fund.apply(c2BCurrency)
        self._fund = fund
        self._stocks = stocks
        self.initial = fund.loc[:start]['BaseAmount'].sum()


    def getInvest(self, end=datetime.date.today()):
        capital = self._fund.loc[:end]['BaseAmount'].sum()
        invest = {
            'capital': capital,
            'bought': 0.0,
            'earning': 0.0,
            'commission': 0.0,
            'tax': 0.0,
        }
            
        value = self.initial
        for s in self._stocks:
            df = s.getStocks(end)
            cost = df['B_Cost'].sum()
            earning = df['Earning'].sum()
            commission = df['Commission_t'].sum() + df['Commission_d'].sum()
            tax = df['Tax_t'].sum() + df['Tax_d'].sum()

            if s.currency != self.currency:
                ex_rate = c.get_rate(s.currency, self.currency, end)
                cost = cost * ex_rate
                earning = earning * ex_rate
                commission = commission * ex_rate
                tax = tax * ex_rate

            invest['bought'] += cost
            invest['earning'] += earning
            invest['commission'] += commission
            invest['tax'] += tax

        return invest


class Stocks:
    '''
    Represent a basket of stocks with their trade & dividend records.
    '''

    def __init__(self, currency, records):
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


    def _selectRows(self, end):
        until = pd.Timestamp(end)

        trades = self._trades.loc[lambda df: df.Date <= until]
        dividends = self._dividends.loc[lambda df: df.Date <= until]
        grp_trade = trades.groupby([trades.index, trades['Transaction']])
        stocks = trades[['Name']].drop_duplicates()
        bs_sum = grp_trade['Qty'].sum().unstack(fill_value=0)
        df = stocks.join(bs_sum)
        df.columns = ['Name', 'B_Qty', 'S_Qty']
        df['Qty'] = df['B_Qty'] + df['S_Qty']

        return df


    def _getTradefee(self, end):
        until = pd.Timestamp(end)

        trades = self._trades.loc[lambda df: df.Date <= until]
        grp_trade = trades.groupby(trades.index)

        return grp_trade[['Commission', 'Tax']].sum()


    def _getDividendfee(self, end):
        until = pd.Timestamp(end)

        dividends = self._dividends.loc[lambda df: df.Date <= until]
        grp_dividend = dividends.groupby(dividends.index)

        return grp_dividend[['Commission', 'Tax']].sum()


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


    def getHolding(self, end=datetime.date.today()):
        df = self._selectRows(end)
        return df[['Name', 'Qty']].loc[lambda df: df.Qty > 0]


    def getStocks(self, end=datetime.date.today()):
        df = self._selectRows(end)

        # Add commission & tax
        df = df.join(self._getTradefee(end))
        df = df.join(self._getDividendfee(end), lsuffix='_t', rsuffix='_d')
        df[['Commission_d', 'Tax_d']].fillna(0.0, inplace=True)

        # Calculate average bought/sold price.
        basis_sum = grp_trade['Basis'].sum().unstack(fill_value=0)
        df['B_Cost'] = basis_sum['BUY'] / df['B_Qty']
        df['S_Cost'] = basis_sum['SELL'] / df['S_Qty'].abs()

        # Calculate dividend for each stock.
        grp_dividend = dividends.groupby(dividends.index)
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
        df['Currency'] = self.currency.upper()

        return df
