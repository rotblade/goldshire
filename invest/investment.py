# -*- coding: utf-8 -*-


import datetime
import pandas as pd
import numpy as np
from pandas.tseries.offsets import *
from config import Config


class Investment:
    """
    Represent long term investment in one base currency.
    """

#   _today = datetime.date.today()
#   _baseday = datetime.date(_today.year, 1, 1) - DateOffset()

    def __init__(self, currency, recfile, pfls,
                 start=datetime.date(2015, 12, 31)):
        """
        :param name: `String` object, a descriptive name.
        :param currency: `String` object, currency of settlement.
        :param recfile: `String` object, csv filename of capital in/out records.
        :param pfls: `List` of `Portfolio` object, potfolios in the investment.
        :param start: `Date` ojbect, the base date to calculate investment
            performance.
        """
        self.currency = currency.upper()
        self.start = start
        self.u2h_rates = pd.read_csv(Config.U2H_RATE_FILE,
                                     parse_dates=['Date'], index_col=0)
        self.portfolios = pfls
        fund_file = Config.CSV_DIR/recfile
        fund_df = pd.read_csv(fund_file, parse_dates=['Date'], index_col=0)
        fund_df['BaseAmount'] = fund_df['Amount'] * fund_df['ExchangeRate']
        self._fund = fund_df
        self.initial = fund_df.loc[:start]['BaseAmount'].sum()


    def __repr__(self):
        return (f'{self.__class__.__name__} - {self.currency}: {self.initial}')


    def getData(self, end=datetime.date.today()):
        """
        Return investment data in a specified day, including initial captial,
        market value, profit/loss and commission/tax.

        :param end: `Date` object, the cut-off date to calculate performance.
        """
        data = {
            #'Currency': self.currency,
            'Fund': self._fund.loc[:end]['BaseAmount'].sum(),
            'Earning': 0.0,
            'Value': 0.0,
            'Market': 0.0,
            'Commission': 0.0,
            'Tax': 0.0,
        }

        for pfl in self.portfolios:
            df = pfl.getStocks(end)
            hold = df.loc[lambda df: df.Qty > 0]

            earning = df['Earning'].sum()
            market = 0.0 if hold.empty else (hold['Last'] * hold['Qty']).sum()
            commission = df['Commission'].sum()
            tax = df['Tax'].sum()

            if pfl.currency == 'USD':
                day = end
                if day not in self.u2h_rates.index:
                    day_stamp = pd.Timestamp(day)
                    if day_stamp > self.u2h_rates.index[0]:
                        day = self.u2h_rates.loc[:day].index[-1]
                    else:
                        raise KeyError(f'No exchange rate found for \
                        {s.currency} on {end}')

                ex_rate = self.u2h_rates.loc[day]['Rate']
                earning = earning * ex_rate
                market = market * ex_rate
                commission = commission * ex_rate
                tax = tax * ex_rate

            data['Earning'] += earning
            data['Market'] += market
            data['Commission'] += commission
            data['Tax'] += tax

        data['Value'] = data['Fund'] + data['Earning']

        data_df = pd.DataFrame(data=data, index=[end])
        data_df.index = pd.to_datetime(data_df.index)
        return data_df.round(2)


    def getPeriodData(self, end=datetime.date.today(), freq='Y'):
        """
        Generate periodic investment data according to frequence.

        :param end: `Date` object, the end date for the period.
        :param freq: `String` object, the frequence of the period. Available
            frequences.
            'Y': Yearly(default)
            'M': Monthly
            'D': Daily
        """
        period_dates = {
            'Y': pd.date_range(start=self.start, end=end, freq='Y'),
            'M': pd.date_range(start=self.start, end=end, freq='M'),
            'D': pd.date_range(start=self.start, end=end, freq='D')[:-1],
        }

        records = []
        for day in period_dates[freq]:
            records.append(self.getData(end=day))
        # data_df = self.getData(end=period_dates[freq][0])
        # for day in period_dates[freq][1:]:
        #     data_df = data_df.append(self.getData(end=day))

        return pd.concat(records)
