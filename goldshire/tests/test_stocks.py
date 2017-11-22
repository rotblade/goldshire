import unittest
from stocks import *
 

class TestStocksMethods(unittest.TestCase):
    def setUp(self):
        files = ('stocks-cny.csv', 'trades-cny.csv', 'dividends-cny.csv')
        self.csvpath = 'csv/'
        self.my_invest = Invest(files, self.csvpath, 'CNY')
        self.my_invest.setdata()

    def test_get_summary(self):
        df = self.my_invest.get_summary()
        self.assertEqual(len(df), 8)
        df = self.my_invest.get_summary(showAll=True)
        self.assertEqual(len(df), 43)

    def test_get_stock(self):
        df = self.my_invest.get_stock('000001')
        print(df)
        self.assertEqual(len(df), 6)


if __name__ == '__main__':
    unittest.main()
