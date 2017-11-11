import pandas as pd
import numpy as np


def get_trade_indicators(stocks, trades, dividends):
    '''
    stocks: A pandas dataframe that lists all traded stocks.
    trades: A pandas dataframe that lists all trades.
    dividends: A pandas dataframe that lists all dividends.
    
    Return a dataframe that includes all useful trade indicators.
    For example, Total buy/sell amount for a stock and average buy/sell price.
    '''

    # Calculate actual amount for each trade.
    proceed = trades['Price'] * trades['Qty'].abs()
    fee = trades['Commission'] + trades['Tax']
    trades['Basis'] = np.where( trades['Transaction']=='BUY',
            proceed+fee, proceed-fee)

    # Claculate total bought/sold qty for each stock.
    group_trade = trades.groupby([trades.index, trades['Transaction']])
    qty_sum = group_trade['Qty'].sum().unstack(fill_value=0)
    stocks_detail = stocks.join(qty_sum)
