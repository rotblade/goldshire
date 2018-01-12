from goldshire import app


@app.route('/')
@app.route('/index')
def index():
    overall = {
        'value': 0.0,
        'position':0.0,
        'free': 0.0,
    }
    invests = [p.getInvest() for p in portfolios.values()]
    for item in invests:
        value = item['value']
        position = item['position']
        if item['currency'] == 'HKD':
            value = item['value'] * h2c_rate
            position = item['position'] * h2c_rate

        overall['value'] += value
        overall['position'] += position

    overall['free']= overall['value'] - overall['position']
    return render_template('index.html', overall=overall)


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
