from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from stocks import csv2df, get_detail


stocks_cny = csv2df('stocks-cny.csv', 'trades-cny.csv', 'dividends-cny.csv')
df_stocks = get_detail(stocks_cny[0], stocks_cny[1], stocks_cny[2])
data_stocks = df_stocks.head(10).to_html(border=0, classes="table")


def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    return app

app = create_app()


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/stocks')
def traded_stocks():
    return render_template('stocks.html', data=data_stocks)
