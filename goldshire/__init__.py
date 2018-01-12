import pandas as pd
from pathlib import Path
from flask import Flask, jsonify, render_template
from models.investment import Invest, Stocks
from config import Config


portfolios = {}
for k, v in Config.FUNDS.items():
    stks = [Stocks(s, stocks[s]) for s in v[2:]]
    portfolios[k] = Invest(v[0], k, v[1], stks)

h2c_rates = pd.read_csv(Config.H2C_RATE_FILE, parse_dates=['Date'], index_col=0)
h2c_rate = h2c_rates.iloc[-1]['Rate']

def create_app():
    app = Flask(__name__)

    return app

app = create_app()

from goldshire import routes
