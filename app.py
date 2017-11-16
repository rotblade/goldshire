from flask import Flask, jsonify, render_template
from flask_bootstrap import Bootstrap
from stocks import csv2df, get_detail, get_summary


stocks_cny = csv2df('stocks-cny.csv', 'trades-cny.csv', 'dividends-cny.csv')
stk_detail = get_detail(stocks_cny[0], stocks_cny[1], stocks_cny[2])


def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stocks/')
def get_stocks():
    stk_summary = get_summary(stk_detail)
    header = ['名称',
              '持仓数量',
              '平均买入价格',
              '已实现盈亏',
              '累计分红']
    stk_summary.columns = header
    #data = stk_summary.to_html(border=0, classes="table", index_names=False)
    data = stk_summary.to_dict(orint='records')
    #return render_template('stocks.html', data=data)
    return jsonify([header, data])


@app.route('/stocks/<symbol>/')
def get_stock(symbol):
    stock = stk_detail.loc[symbol]
    return jsonify(stock.to_dict())
