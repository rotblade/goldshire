from datetime import date, timedelta
from config import Config
from helper import get_forexrate, record2file


if __name__ == '__main__':
    yesterday = date.today() - timedelta(1)
    api_url = Config.LAYER_HISTURL
    params = {'access_key': Config.LAYER_KEY, 'date': yesterday}
    forex_rates = get_forexrate(api_url, params)
    usd2hkd = round(forex_rates['USDHKD'], 6)
    record2file(Config.U2H_RATE_FILE, {'Rate': usd2hkd}, day=yesterday)
    hkd2cny = round(forex_rates['USDCNY']/forex_rates['USDHKD'], 6)
    record2file(Config.H2C_RATE_FILE, {'Rate': hkd2cny}, day=yesterday)
