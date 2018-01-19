# -*- coding: utf-8 -*-

from pathlib import Path


basedir = Path(__file__).absolute().parent


class Config:
    TENCENT_URL = 'http://qt.gtimg.cn/q=s_'
    NOWAPI_URL = 'http://api.k780.com'
    NOWAPI_KEY = '30005'
    NOWAPI_SIGN = 'ad3bec0960a7590fe5422d110b4337a2'
    # ALPHAVANTAGE_URL = 'https://www.alphavantage.co/query'
    # ALPHAVANTAGE_KEY = '24JJSPF9FOR8DS08'
    # ONEFORGE_URL = 'https://forex.1forge.com/1.02/quotes'
    # ONEFORGE_KEY = 'apE1SnpinUYfteiVG4K9v8z7WvAd9Unj'
    # OEXRATE_KEY = '33de76c4526743dd99604bbe22bc508d'
    LAYER_URL = 'http://apilayer.net/api/live'
    LAYER_HISTURL = 'http://apilayer.net/api/historical'
    LAYER_KEY = 'f88661c6bfc9ee095f453d8c78b96a6a'
    CSV_DIR = basedir/'goldshire'/'csv'
    HISTORIC_DIR = CSV_DIR/'historic'
    H2C_RATE_FILE = CSV_DIR/'rate-hkd2cny.csv'
    U2H_RATE_FILE = CSV_DIR/'rate-usd2hkd.csv'
    STOCKS = {
        'cny': ['trades-cny.csv', 'dividends-cny.csv'],
        'hkd': ['trades-hkd.csv', 'dividends-hkd.csv'],
        'usd': ['trades-usd.csv', 'dividends-usd.csv'],
    }
    FUNDS = {
        'cny': ['fund-domestic.csv', 'cny'],
        'hkd': ['fund-oversea.csv', 'hkd', 'usd'],
    }
