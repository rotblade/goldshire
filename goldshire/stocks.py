from helper import csv2df, get_tx_quotes


class Invest:
    '''
    Represent long term investment in one currency.
    '''
    def __init__(self, files, currency):
        self.data = csv2df(files)
        self.currency = currency

    def __repr__(self):
        return (f'{slef.__class__.__name__} - {self.currency}')


def get_static(stocks, trades, divids):
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
    trades['Basis'] = np.where(trades['Transaction'] == 'BUY',
                               proceed + fee, proceed - fee)

    # Generate Pandas groupby object for trades and dividends.
    group_trade = trades.groupby([trades.index, trades['Transaction']])
    group_divid = divids.groupby(divids.index)

    # Claculate total bought/sold qty for each stock.
    qty_sum = group_trade['Qty'].sum().unstack(fill_value=0)
    s_df = stocks.join(qty_sum)
    s_df.columns = ['Name', 'Hold', 'B_Qty', 'S_Qty']
    s_df['Qty'] = s_df['B_Qty'] + s_df['S_Qty']

    # Calculate average bought/sold price.
    basis = group_trade['Basis'].sum().unstack(fill_value=0)
    s_df['B_Cost'] = basis['BUY'] / s_df['B_Qty']
    s_df['S_Cost'] = basis['SELL'] / s_df['S_Qty'].abs()

    # Calculate realized profit/loss
    sold_cost = s_df['B_Cost'] * s_df['S_Qty'].abs()
    s_df['R_PnL'] = basis['SELL'] - sold_cost

    # Calculate dividend for each stock.
    divid_fee = divids['Commission'] + divids['Tax']
    divids['Dividend'] = divids['PerShare'] * divids['Qty'] - divid_fee
    s_df['Dividend'] = group_divid['Dividend'].sum()

    # Fill NaN with zero value for realized profit/loss and dividend.
    s_df['R_PnL'].fillna(0.0, inplace=True)
    s_df['Dividend'].fillna(0.0, inplace=True)

    return s_df.reset_index()
    # return s_df


def get_detail(s_df, isA=True):
    '''
    '''
    hold = s_df.loc[lambda df: df.Qty > 0]
    quotes = get_tx_quotes(hold.index, isA)
    detail = s_df.join(quotes)

    # Calculate unrealized profit/loss for holding stocks.
    detail['UR_PnL'] = detail['Qty'] * (detail['Last'] - detail['B_Cost'])

    # Fill unrealized profit/loss NaN with zero value for all not hold stocks.
    detail['UR_PnL'].fillna(0.0, inplace=True)

    # Calculate total earning for each stock.
    detail['Earning'] = detail['Dividend'] + detail['R_PnL'] + detail['UR_PnL']

    # Calculate total earning for each stock.
    detail['Return'] = detail['Earning'] / (detail['B_Qty'] * detail['B_Cost'])

    return detail.round(2)



def get_summary(df, showAll=False):
    '''
    Get stocks summary.
    '''
    # Show only holding stocks by default
    hold = df.loc[lambda df: df.Qty > 0] if not showAll else detail

    # Extract useful summary fields.
    summary = hold[['Symbol', 'Name', 'Qty', 'Last', 'Percent', 'Earning', 'Return']]

    return summary
