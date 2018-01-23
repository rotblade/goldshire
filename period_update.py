import datetime
import pandas as pd
from config import Config
from invest import Portfolio, Investment
from helper import get_forexrate, record2file


if __name__ == '__main__':
    # Update daily exchange rate for USD2HKD and HKD2CNY
    yesterday = datetime.date.today() - timedelta(1)
    api_url = Config.LAYER_HISTURL
    params = {'access_key': Config.LAYER_KEY, 'date': yesterday}
    forex_rates = get_forexrate(api_url, params)
    usd2hkd = round(forex_rates['USDHKD'], 6)
    record2file(Config.U2H_RATE_FILE, {'Rate': usd2hkd}, day=yesterday)
    hkd2cny = round(forex_rates['USDCNY']/forex_rates['USDHKD'], 6)
    record2file(Config.H2C_RATE_FILE, {'Rate': hkd2cny}, day=yesterday)

    # Update daily, monthly and yearly investment data.
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
