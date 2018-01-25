from datetime import date, timedelta
from config import Config
from invest import Portfolio
from helper import get_tx_quotes, get_forexrate, record2file


if __name__ == '__main__':
    # Update stocks' daily close price.
    today = date.today()
    holdings = []
    for k, v in Config.STOCKS.items():
        pfl = Portfolio(k, Config.STOCKS[k])
        holdings.append(pfl.getHolding(today))

    for symbols in holdings:
        if len(symbols) > 0:
            quotes = get_tx_quotes(symbols.index)
            for i, row in quotes.iterrows():
                record2file(Config.HISTORIC_DIR/f'{i}.csv',
                            {'Close':row['Last']})
