import datetime
from config import Config
from invest.portfolio import Portfolio
from helper import get_tx_quotes, quotes2csvs


if __name__ == '__main__':
    today = datetime.date.today()
    holdings = {}
    for k, v in Config.STOCKS.items():
        pfl = Portfolio(k, Config.STOCKS[k])
        holdings[k] = pfl.getHolding(today)

    for k, v in holdings.items():
        if len(v) > 0:
            quotes = get_tx_quotes(v.index, market=k)
            quotes2csvs(quotes['Last'], today.strftime('%Y-%m-%d'),
                        Config.HISTORIC_DIR)
