import pandas as pd
import numpy as np


def csv2df(csv_stock, csv_trade, csv_divid):
    stocks = pd.read_csv('csv/' + csv_stock, dtype={'Symbol':str})
    trades = pd.read_csv(
        'csv/' + csv_trade,
        dtype={'Symbol':str, 'Qty':np.int64}
        )
    divids = pd.read_csv(
        'csv/' + csv_divid,
        dtype={'Symbol':str,'Qty':np.int64}
        )
    
    return (stocks, trades, divids)


def get_summary(stocks, trades, divids):
    '''
    stocks: A pandas dataframe that lists all traded stocks.
    trades: A pandas dataframe that lists all trades.
    dividends: A pandas dataframe that lists all dividends.

    Return a dataframe that includes all useful trade indicators.
    For example, Total buy/sell amount for a stock and average buy/sell price.
    '''

    # Set stock's symbol as Dataframe index.
    stocks.set_index('Symbol', inplace=True)
    trades.set_index('Symbol', inplace=True)
    divids.set_index('Symbol', inplace=True)

    # Calculate actual amount for each trade.
    proceed = trades['Price'] * trades['Qty'].abs()
    fee = trades['Commission'] + trades['Tax']
    trades['Basis'] = np.where( trades['Transaction']=='BUY',
            proceed+fee, proceed-fee)

    # Generate Pandas groupby object for trades and dividends.
    group_trade = trades.groupby([trades.index, trades['Transaction']])
    group_divid = divids.groupby(divids.index)

    # Claculate total bought/sold qty for each stock.
    qty_sum = group_trade['Qty'].sum().unstack(fill_value=0)
    stocks_detail = stocks.join(qty_sum)
    stocks_detail.columns = ['Name', 'B_Qty', 'S_Qty']

    # Calculate average bought/sold price.
    basis = group_trade['Basis'].sum().unstack(fill_value=0)
    stocks_detail['B_Cost'] = basis['BUY']/stocks_detail['B_Qty']
    stocks_detail['S_Cost'] = basis['SELL']/stocks_detail['S_Qty'].abs()

    # Calculate realized profit/loss
    sold_cost = stocks_detail['B_Cost'] * stocks_detail['S_Qty'].abs()
    stocks_detail['R_PnL'] = basis['SELL']- sold_cost

    # Calculate dividend for each stock.
    divid_fee = divids['Commission'] + divids['Tax']
    divids['Dividend'] = divids['PerShare']*divids['Qty'] - divid_fee
    stocks_detail['Dividend'] = group_divid['Dividend'].sum()

    # Fill NaN with zero value for realized profit/loss and dividend.
    stocks_detail['R_PnL'].fillna(0.0, inplace=True)
    stocks_detail['Dividend'].fillna(0.0, inplace=True)

    return stocks_detail.reset_index().round(2)
