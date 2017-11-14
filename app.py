from flask import Flask, render_template
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


@app.route('/stocks')
def traded_stocks():
    stk_summary = get_summary(stk_detail)
    stk_summary.columns = ['名称',
                           '持仓数量',
                           '平均买入价格',
                           '已实现盈亏',
                           '累计分红', ]
    data = stk_summary.to_html(border=0, classes="table", index_names=False)
    return render_template('stocks.html', data=data)
