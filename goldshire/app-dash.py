# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from stocks import get_trade_indicators


import pandas as pd
import numpy as np

stocks_cny = pd.read_csv('csv/stocks-cny.csv', dtype={'Symbol':str})
trades_cny = pd.read_csv(
        'csv/trades-cny.csv',
        dtype={'Symbol':str, 'Qty':np.int64}
        )
dividends_cny = pd.read_csv(
        'csv/dividends-cny.csv',
        dtype={'Symbol':str,'Qty':np.int64}
        )

stocks_hkd = pd.read_csv('csv/stocks-hkd.csv', dtype={'Symbol':str})
trades_hkd = pd.read_csv(
        'csv/trades-hkd.csv',
        dtype={'Symbol':str, 'Qty':np.int64}
        )
dividends_hkd = pd.read_csv(
        'csv/dividends-hkd.csv',
        dtype={'Symbol':str, 'Qty':np.int64}
        )


def generate_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr(
            [html.Td(df.iloc[i][col]) for col in df.columns]
        ) for i in range(len(df))],
        className='table'
    )


app = dash.Dash()
bootstrap_min_url = \
        "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
bootstrap_theme_url = \
        "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css"
app.css.append_css({"external_url": bootstrap_min_url})
app.css.append_css({"external_url": bootstrap_theme_url})

df = get_trade_indicators(stocks_cny, trades_cny, dividends_cny)

app.layout = html.Div([
    html.Div([
        html.H3('Traded Stocks'),
    ], className='jumbotron'),
    html.Div([
        html.Div([
            generate_table(df.head())
        ], className='col-md-12')
    ], className='row'),
    html.Div([
    ], className='well')
], className='container')


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
