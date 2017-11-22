from flask import Flask, jsonify, render_template
#from flask_bootstrap import Bootstrap
from stocks import Invest


cnyfiles = ('stocks-cny.csv', 'trades-cny.csv', 'dividends-cny.csv')
hkdfiles = ('stocks-hkd.csv', 'trades-hkd.csv', 'dividends-hkd.csv')
usdfiles = ('stocks-usd.csv', 'trades-usd.csv', 'dividends-usd.csv')

invest_cny = new Invest(cnyfiles, 'CNY')
invest_hkd = new Invest(hkdfiles, 'HKD')
invest_usd = new Invest(usdfiles, 'USD')


def create_app():
    app = Flask(__name__)
    # Bootstrap(app)

    return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stocks/')
def get_stocks():
    header = ['代码',
              '名称',
              '持仓数量',
              '最后价格',
              '盈亏',
              '回报']

    summary = {
        'CNY': invest_cny.get_summary.to_dict(orient='records'),
        'HKD': invest_hkd.get_summary.to_dict(orient='records'),
        'USD': invest_usd.get_summary.to_dict(orient='records')
    }

    for key in summary:
        summary[key].columns = header

    return summary
    #data = stk_summary.to_html(border=0, classes="table", index_names=False)
    #data = stk_summary.to_dict(orient='records')
    #return render_template('stocks.html', data=data)
    #return jsonify([header, data])


@app.route('/stocks/<symbol>/')
def get_stock(symbol):
    stock = invest_cny.get_stock(symbol)
    if Invest.whichmarket(symbol) == 'hk':
        stock = invest_cny.get_stock(symbol)
    if Invest.whichmarket(symbol) == 'us':
        stock = invest_hkd.get_stock(symbol)

    return jsonify(stock.to_dict())
