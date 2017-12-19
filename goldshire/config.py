# -*- coding: utf-8 -*-

import configparser


config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read('settings.conf')

csvpath = config['Path']['csvpath']

funds = {}
for k in config['Funds']:
    funds[k] = [v for v in config['Funds'][k].split(',')]

stocks = {}
for k in config['Stocks']:
    stocks[k] = [v for v in config['Stocks'][k].split(',')]
