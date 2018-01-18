import datetime
from config import Config
from invest.portfolio import Portfolio
from helper import get_tx_quotes, quotes2csvs


if __name__ == '__main__':
    invests = []
    for k, v in Config.FUNDS.items():
        pfls = [Portfolio(c, Config.STOCKS[c]) for c in v[1:]]
        invests.append(Investment(k, v[0], pfls))

    end = datetime.date.today()
    period_cny = invests[0].getPeriodData(freq='D')[['Earning', 'Market',
                                                     'Value', 'Commission',
                                                     'Tax']]
    period_hkd = invests[1].getPeriodData(freq='D')[['Earning', 'Market',
                                                     'Value', 'Commission',
                                                     'Tax']]
