import unittest
import datetime
from goldshire.config import csvpath, stocks
from goldshire.investment import Stocks


class TestStocks(unittest.TestCase):
    def setUp(self):
        self.before = datetime.date(2017, 2, 1)
        self.today = datetime.date.today()
        self.pfl = {}
        for k, v in stocks.items():
             self.pfl[k] = Stocks(k, stocks[k])

    def test_new(self):
        for v in self.pfl.values():
            self.assertTrue(len(v._trades) > 0)
            self.assertTrue(len(v._dividends) > 0)

    def test_preCal(self):
        df = self.pfl['hkd']._preCal(self.before)
        fields = ['Name', 'Qty', 'B_Cost']
        for field in fields:
            self.assertTrue(field in df.columns)

    def test_getTrade(self):
        s_df = self.pfl['cny']._preCal(self.before)
        df = self.pfl['cny']._getTrade(s_df, self.before)
        fields = ['R_PnL', 'Last', 'UR_PnL', 'Commission', 'Tax']
        for field in fields:
            self.assertTrue(field in df.columns)

    def test_getDividend(self):
        df = self.pfl['cny']._getDividend(self.before)
        fields = ['Commission', 'Tax', 'Dividend']
        for field in fields:
            self.assertTrue(field in df.columns)

    def test_getPrice(self):
        symbols = ['000895', '600585', '600660']
        prices = Stocks.getPrice(csvpath, symbols, self.before)
        self.assertEqual(prices.iloc[0], 21.40)
        self.assertEqual(prices.iloc[1], 19.93)
        self.assertEqual(prices.iloc[2], 18.80)

    def test_getHolding(self):
        holding = self.pfl['hkd'].getHolding(self.today)
        self.assertTrue(len(holding) > 0 and len(holding) < 10)

    def test_getStocks(self):
        df = self.pfl['cny'].getStocks(self.before)
        fields = ['Commission_t', 'Tax_t', 'Commission_d', 'Tax_d', 'Earning', 'Return']
        for field in fields:
            self.assertTrue(field in df.columns)
        #print(stocks.head(10))

if __name__ == '__main__':
    unittest.main()
