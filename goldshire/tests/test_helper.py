import unittest
import pandas as pd
import datetime
from helper import *
 

class TestHelperMethods(unittest.TestCase):
    def setUp(self):
        self.df1 = pd.read_csv('csv/stocks-cny.csv')
        self.df2 = pd.read_csv('csv/trades-cny.csv')
        self.df3 = pd.read_csv('csv/dividends-cny.csv')
        self.files = ('stocks-cny.csv',
                      'trades-cny.csv',
                      'dividends-cny.csv')
        self.codes = pd.Series('000001')
        self.quote = pd.Series(23.76, index=['888888'])
        self.csvpath = 'tests/'
        self.today = datetime.date.today().strftime('%Y-%m-%d')

    def test_csv2df(self):
        dfs = csv2df(self.files)
        self.assertEqual(len(self.df1), len(dfs[0]))
        self.assertEqual(len(self.df2), len(dfs[1]))
        self.assertEqual(len(self.df3), len(dfs[2]))

    def test_quotes2csvs(self):
        quotes2csvs(self.quote, self.today, self.csvpath)
        df = pd.read_csv(self.csvpath + '888888.csv')
        self.assertEqual(df.iloc[-1, 0], self.today)
        self.assertEqual(df.iloc[-1, 1], 23.76)

    def test_get_lastprice(self):
        self.assertEqual(get_lastprice('888888', self.csvpath), 23.76)

    def test_get_tx_quotes(self):
        df = get_tx_quotes(self.codes)
        print(df)
        self.assertTrue(len(df) > 0)


if __name__ == '__main__':
    unittest.main()
