import json

from pandas import DataFrame
import pandas_datareader as web

from config import START_DATE, END_DATE


def get_crypto_currency(from_currency='eth', to_currency='usd') -> dict:
    crypt_currency = {}
    eth = web.DataReader(f'{from_currency.upper()}-{to_currency.upper()}', 'yahoo', START_DATE, END_DATE)
    df = DataFrame(eth, columns=['Adj Close'])
    for datetime, row in df.iterrows():
        datetime = str(datetime).split()[0]
        crypt_currency[datetime] = float(round(row[-1], 3))
    return crypt_currency

