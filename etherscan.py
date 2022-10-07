import json
from datetime import datetime

import requests

from config import API_KEY, WALLET_ADDRESS, BASE_URL, ETH_VALUE, GWEI_VALUE, START_DATE, END_DATE, save_scv, \
    change_value
from crypto_currency import get_crypto_currency


def make_api_url(module: str, action: str, address: str, **kwargs) -> str:
    url = BASE_URL + f'?module={module}&action={action}&address={address}&apikey={API_KEY}'
    for key, value in kwargs.items():
        url += f'&{key}={value}'
    return url


def get_balance(address: str) -> int:
    balance_url = make_api_url('account', 'balance', address, tag='latest')
    return int(requests.get(balance_url).json()['result']) / ETH_VALUE


def get_transactions(address: str) -> dict:
    transactions_url = make_api_url('account', 'txlist', address, startblock=0, endblock=99999999,
                                    page=1, offset=10000, sort='asc')
    data = requests.get(transactions_url).json()['result']
    current_balance = 0
    out_balance = 0
    in_balance = 0
    balances = []
    dates = []
    for tx in data:
        value = int(tx['value']) / ETH_VALUE
        gas = int(tx['gasUsed']) * int(tx['gasPrice']) / ETH_VALUE
        date = datetime.fromtimestamp(int(tx['timeStamp']))
        if START_DATE < date < END_DATE:
            if tx['to'].lower() == address.lower():
                current_balance += value
                in_balance += value
            else:
                current_balance -= value + gas
                out_balance += value
        balances.append(current_balance)
        dates.append(date)
    # plt.plot(times, balances)
    # plt.show()
    return {'current_balance': current_balance, 'in_balance': in_balance, 'out_balance': out_balance}


def get_erc20_tx(address, contract_address):
    transactions_url = make_api_url('account', 'tokentx', address,
                                    contractaddress=contract_address,
                                    startblock=0, endblock=27025780,
                                    page=1, offset=100, sort='asc')
    return requests.get(transactions_url).json()['result']


def get_dataset_for_graph(address: str):
    transactions_url = make_api_url('account', 'txlist', address, startblock=0, endblock=99999999,
                                    page=1, offset=10000, sort='asc')
    data = requests.get(transactions_url).json()['result']
    edges = {}
    edges_lst = []
    in_address = set()
    out_address = set()
    for counter, tx in enumerate(data):
        to_address = tx['to']
        from_address = tx['from']
        date = datetime.fromtimestamp(int(tx['timeStamp']))
        if START_DATE < date < END_DATE:
            for date_cur, exch_rate in get_crypto_currency().items():
                if str(date).split()[0] == date_cur:
                    edges.update({counter: {}})
                    if int(tx['value']) == 0:
                        for tx_contract in get_erc20_tx(WALLET_ADDRESS, to_address):
                            if tx['hash'] == tx_contract['hash']:
                                edges[counter].update({
                                    'block_number': int(tx_contract['blockNumber']),
                                    'from': tx_contract['from'],
                                    'to': tx_contract['contractAddress'],
                                    'coin_name': tx_contract['tokenName'],
                                    'value': int(tx_contract['value']),
                                    'gas': int(tx_contract["gasPrice"]) / GWEI_VALUE,
                                    'date': str(date),
                                    'value_usd': int(tx_contract['value']) / 10 ** int(tx_contract['tokenDecimal']),
                                    'exch_rate': exch_rate
                                })
                    else:
                        edges[counter].update({
                            'block_number': int(tx['blockNumber']),
                            'from': from_address,
                            'to': to_address,
                            'coin_name': 'ETH',
                            'value': int(tx['value']) / ETH_VALUE,
                            'gas': (int(tx['gasPrice'])) / GWEI_VALUE,
                            'date': str(date),
                            'value_usd': round(exch_rate * (int(tx['value']) / ETH_VALUE), 3),
                            'exch_rate': exch_rate
                        })
            edges_lst.append((from_address, to_address, 3))
            edges['final_edges'] = edges_lst
            if to_address == address.lower():
                in_address.add(from_address)

            else:
                out_address.add(to_address)
    return {'nodes': {'current_address': address.lower(), 'in': list(in_address), 'out': list(out_address)},
            'edges': edges}


def main() -> None:
    m_d = get_dataset_for_graph(WALLET_ADDRESS.lower())
    print(json.dumps(m_d, indent=3))
    return save_scv(m_d)


if __name__ == '__main__':
    pass
    # main()
