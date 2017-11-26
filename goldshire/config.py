import configparser


config = configparser.ConfigParser()
config.read('settings.conf')

csvpath = config['Path']['csvpath']

funds = {}
for k in config['Funds']:
    funds[k] = csvpath + config['Funds'][k]

stocks = {}
for k in config['Stocks']:
    stocks[k] = [csvpath+v for v in config['Stocks'][k].split(',')]
