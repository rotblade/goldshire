import pandas as pd
from flask import Flask
from invest import Portfolio, Investment, Currency
from config import Config

invests = {}
for k, v in Config.FUNDS.items():
    pfls = [Portfolio(c, Config.STOCKS[c]) for c in v[1:]]
    invests[k] = Investment(k, v[0], pfls)

HKD = Currency('hkd', Config.H2C_RATE_FILE)

def create_app():
    app = Flask(__name__)

    return app

app = create_app()

from app import routes
