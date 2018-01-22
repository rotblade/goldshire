import datetime
from flask import jsonify, render_template
from app import app, invests, HKD


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
