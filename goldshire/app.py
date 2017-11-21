from flask import Flask, jsonify, render_template
#from flask_bootstrap import Bootstrap
from stocks import csv2df, get_detail, get_summary


stocks_cny = csv2df('stocks-cny.csv', 'trades-cny.csv', 'dividends-cny.csv')
stocks_hkd = csv2df('stocks-hkd.csv', 'trades-hkd.csv', 'dividends-hkd.csv')
stocks_usd = csv2df('stocks-usd.csv', 'trades-usd.csv', 'dividends-usd.csv')

detail_cny = get_detail(stocks_cny[0], stocks_cny[1], stocks_cny[2])
detail_hkd = get_detail(stocks_hkd[0], stocks_hkd[1], stocks_hkd[2])
detail_usd = get_detail(stocks_usd[0], stocks_usd[1], stocks_usd[2])


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
              '当前价格',
              '盈亏',
              '收益率']

    summary = {
        'CNY': get_summary(detail_cny).to_dict(orient='records'),
        'HKD': get_summary(detail_hkd).to_dict(orient='records'),
        'USD': get_summary(detail_usd).to_dict(orient='records')
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
    stock = stk_detail.loc[symbol]
    return jsonify(stock.to_dict())
