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

    # Update daily exchange rate for USD2HKD and HKD2CNY
    yesterday = today - timedelta(1)
    api_url = Config.LAYER_HISTURL
    params = {'access_key': Config.LAYER_KEY, 'date': yesterday}
    forex_rates = get_forexrate(api_url, params)
    usd2hkd = forex_rates['USDHKD']
    record2file(Config.U2H_RATE_FILE, {'Rate': usd2hkd}, day=yesterday)
    hkd2cny = round(forex_rates['USDCNY']/forex_rates['USDHKD'], 6)
    record2file(Config.H2C_RATE_FILE, {'Rate': hkd2cny}, day=yesterday)
