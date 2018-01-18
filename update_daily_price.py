import datetime
from config import Config
from invest.portfolio import Portfolio
from helper import get_tx_quotes, quotes2csvs


if __name__ == '__main__':
    today = datetime.date.today()
    holdings = []
    for k, v in Config.STOCKS.items():
        pfl = Portfolio(k, Config.STOCKS[k])
        holdings.append(pfl.getHolding(today))

    for symbols in holdings:
        if len(symbols) > 0:
            quotes = get_tx_quotes(symbols.index)
            quotes2csvs(quotes['Last'], today.strftime('%Y-%m-%d'),
                        Config.HISTORIC_DIR)
