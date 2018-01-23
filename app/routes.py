import datetime
from flask import jsonify, render_template
from app import app, invests, HKD

columns = [
    'Name',
    'Qty',
    'Last',
    'Market',
    'R_PnL',
    'UR_PnL',
    'Dividend',
    'Earning',
    'Return',
    'Commission',
    'Tax',
]

headers = [
    '股票代码',
    '股票名称',
    '持仓数量',
    '最后价格',
    '市值',
    '已实现盈亏',
    '未实现盈亏',
    '累计分红',
    '总盈亏',
    '回报率',
    '累计佣金',
    '累计税金',
]

@app.route('/')
@app.route('/index')
def index():
    day = datetime.date.today()
    df_cny = invests['cny'].getData(day)
    df_hkd = invests['hkd'].getData(day)
    df_all= df_cny + (df_hkd*HKD.get_rate2cny(day)).round(2)
    rec_cny = df_cny.to_dict(orient='records')[0]
    rec_hkd = df_hkd.to_dict(orient='records')[0]
    rec_all = df_all.to_dict(orient='records')[0]

    return render_template('index.html', data_cny=rec_cny, data_hkd=rec_hkd,
                            data_all=rec_all)


@app.route('/stocks/')
def get_stocks():
    day = datetime.date.today()
    df_cny = invests['cny'].portfolios[0].getStocks(day)[columns]
    df_hkd = invests['hkd'].portfolios[0].getStocks(day)[columns]
    df_usd = invests['hkd'].portfolios[1].getStocks(day)[columns]

    stocks={}
    stocks['cny'] = df_cny.to_dict(orient='index')
    stocks['hkd'] = df_hkd.to_dict(orient='index')
    stocks['usd'] = df_usd.to_dict(orient='index')

    # return jsonify([headers, stocks])
    return render_template('stocks.html', headers=headers, stocks=stocks)


@app.route('/stocks/<symbol>/')
def get_stock(symbol):
    currency = Invest.whichMarket(symbol)
    stock = invest[currency].get_stock(symbol)

    return jsonify(stock.to_dict())
