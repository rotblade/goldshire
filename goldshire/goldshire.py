import pandas as pd
from flask import Flask, jsonify, render_template
from .stocks import Invest


cnyfiles = ('stocks-cny.csv', 'trades-cny.csv', 'dividends-cny.csv')
hkdfiles = ('stocks-hkd.csv', 'trades-hkd.csv', 'dividends-hkd.csv')
usdfiles = ('stocks-usd.csv', 'trades-usd.csv', 'dividends-usd.csv')

csvpath = 'goldshire/csv/'

invest = {
    'CNY': Invest(cnyfiles, csvpath, 'CNY'),
    'HKD': Invest(hkdfiles, csvpath, 'HKD'),
    'USD': Invest(usdfiles, csvpath, 'USD'),
}

for v in invest.values():
    v.setdata()


def create_app():
    app = Flask(__name__)

    return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stocks/')
def get_stocks():
    header = [
        '代码',
        '股票',
        '币种',
        '持仓数量',
        '最后价格',
        '盈亏',
        '回报',
    ]

    summary = {}
    for k, v in invest.items():
        summary[k] = v.get_summary()
        summary[k].columns = header
    result = pd.concat(list(summary.values()), ignore_index=True)

    return jsonify([header, result.to_dict(orient='records')])
    #data = stk_summary.to_html(border=0, classes="table", index_names=False)
    #data = stk_summary.to_dict(orient='records')
    #return render_template('stocks.html', data=data)


@app.route('/stocks/<symbol>/')
def get_stock(symbol):
    currency = Invest.whichMarket(symbol)
    stock = invest[currency].get_stock(symbol)

    return jsonify(stock.to_dict())
