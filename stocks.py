import datetime
import pandas as pd
import numpy as np
import tushare as ts


def csv2df(csv_stock, csv_trade, csv_divid):
    '''
    csv_stock: CSV file that includes traded stocks info.
    csv_trade: CSV file that includes all trades info.
    csv_divid: CSV file that includes dividend info.

    Return: A tuple with converted Pandas dataframe for the 3 CSV files.
    '''
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


def get_ts_quote(symbols, isA=True):
    cons = ts.get_apis()
    last = datetime.datetime.today() - datetime.timedelta(days=7)

    quotes_dict = {}
    for item in symbols:
        if isA:
            df = ts.bar(item, conn=cons, freq='D',
                start_date=last, end_date='')
        else:
            df = ts.bar(item, conn=cons, asset='X',
                start_date=last, end_date='')
        quotes_dict[item] = df['close'].iloc[0]

    quotes = pd.Series(quotes_dict)
    return quotes


def get_detail(stocks, trades, divids):
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
    stocks_detail['Qty'] = stocks_detail['B_Qty'] + stocks_detail['S_Qty']

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

#    # Get latest price for the holding stocks.
#    hold = stocks_detail.loc[lambda df: df.Qty > 0]
#    ts_last = get_ts_quote(hold.index)
#    stocks_detail['Last'] = ts_last
#
#    # Calculate unrealized profit/loss for holding stocks.
#    stocks_detail['UR_PnL'] = stocks_detail['Qty'] * \
#                            (stocks_detail['Last'] - stocks_detail['B_Cost'])
#
#    # Calculate total earning for each stock.
#    stocks_detail['Earning'] = stocks_detail['Dividend'] + \
#                            stocks_summary['R_PnL'] + stocks_summary['UR_PnL']

    #return stocks_detail.reset_index().round(2)
    return stocks_detail.round(2)


def get_summary(detail, showAll=False):
    '''
    Get stocks summary from detail information.
    '''
    # Show only holding stocks by default
    summary = detail.loc[lambda df: df.Qty > 0] if not showAll else detail

    # Extract useful summary fields.
    df = summary[['Name', 'Qty', 'B_Cost', 'R_PnL', 'Dividend']]

    return df
