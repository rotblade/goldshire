import datetime
from pathlib import Path
from config import stocks
from investment import Stocks
from helper import get_tx_quotes, quotes2csvs


if __name__ == '__main__':
    today = datetime.date.today()
    pwd = Path.cwd()
    holdings = {}
    for k, v in stocks.items():
        pfl = Stocks(k, stocks[k])
        holdings[k] = pfl.getHolding(today)

    for k, v in holdings.items():
        if len(v) > 0:
            quotes = get_tx_quotes(v.index, market=k)
            quotes2csvs(quotes['Last'], today.strftime('%Y-%m-%d'),
                        pwd/'csv'/'historic')
