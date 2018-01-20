import datetime
import pandas as pd
from config import Config
from invest.portfolio import Portfolio
from helper import record2file


if __name__ == '__main__':
    invests = []
    for k, v in Config.FUNDS.items():
        pfls = [Portfolio(c, Config.STOCKS[c]) for c in v[1:]]
        invests.append(Investment(k, v[0], pfls))

    period_cny = invests[0].getData()[['Fund', 'Earning', 'Value', 'Market',
                                       'Commission', 'Tax']]
    period_hkd = invests[1].getData()[['Fund', 'Earning', 'Value', 'Market',
                                       'Commission', 'Tax']]

    record2file(Config.DAILY_CNY_FILE, period_cny.values[0])
    record2file(Config.DAILY_HKD_FILE, period_hkd.values[0])

    day = pd.Timestamp(datetime.date.today())
    if day.is_month_end:
        record2file(Config.MONTHLY_CNY_FILE, period_cny.values[0])
        record2file(Config.MONTHLY_HKD_FILE, period_hkd.values[0])

    if day.is_year_end:
        record2file(Config.YEARLY_CNY_FILE, period_cny.values[0])
        record2file(Config.YEARLY_HKD_FILE, period_hkd.values[0])
