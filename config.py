# -*- coding: utf-8 -*-

from pathlib import Path


basedir = Path(__file__).absolute().parent


class Config:
    TENCENT_QUOTE_URL = 'http://qt.gtimg.cn/q=s_'
    ALPHAVANTAGE_URL = 'https://www.alphavantage.co/query'
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
