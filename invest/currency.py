import datetime
import pandas as pd
from config import Config


class Currency:
    """
    """
    def __init__(self, name, ratefile):
        self.name = name.upper()
        self.rates2cny = pd.read_csv(ratefile, parse_dates=['Date'],
                                     index_col=0)

    def get_rate2cny(self, day=datetime.date.today()):
        if day in self.rates2cny.index:
            return self.rates2cny.loc[day, 'Rate']
        else:
            day_stamp = pd.Timestamp(day)
            if day_stamp > self.rates2cny.index[0]:
                return self.rates2cny.loc[:day].iloc[-1]['Rate']
            else:
                raise KeyError(f'No exchange rate found on {day}')
