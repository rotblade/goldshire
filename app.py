# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html


import pandas as pd


df_stocks_cny = pd.read_csv('csv/stocks-cny.csv', dtype={'Symbol':str})


def generate_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr(
            [html.Td(df.iloc[i][col]) for col in df.columns]
        ) for i in range(len(df))]
    )


app = dash.Dash()


app.layout = html.Div(children=[
    html.H1('Traded Stocks'),
    generate_table(df_stocks_cny)
])


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
