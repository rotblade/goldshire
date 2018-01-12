import unittest
import datetime
from goldshire.config import *
from goldshire.investment import Invest, Stocks


class TestInvest(unittest.TestCase):
    def setUp(self):
        self.before = datetime.date(2016, 12, 31)
        self.today = datetime.date.today()
        self.fnds = {}
        for k, v in funds.items():
            stks = [Stocks(s, stocks[s]) for s in v[2:]]
            self.fnds[k] = Invest(v[0], k, v[1], stks)

    def test_new(self):
        for v in self.fnds.values():
            self.assertTrue(v.initial > 0)

    def test_getInvest(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        invest = {}
        for k, v in self.fnds.items():
            invest[k] = v.getInvest(self.before)
        pp.pprint(invest)
        invest = {}
        for k, v in self.fnds.items():
            invest[k] = v.getInvest(self.today)
        pp.pprint(invest)

if __name__ == '__main__':
    unittest.main()
