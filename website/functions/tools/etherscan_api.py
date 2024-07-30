import requests

def get_ethereum_balance(api_key, address):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':
            balance = data['result']
            return int(balance)
        else:
            raise ValueError(f"Error from Etherscan API: {data['message']}")
    else:
        response.raise_for_status()

def wei_to_ether(wei):
    return wei / 10**18

def get_eth_to_usd_rate():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "ethereum",
        "vs_currencies": "usd"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['ethereum']['usd']
    else:
        return {'error', response}

def get_ethereum_balance_usd(api_key, address):
    wei_balance = get_ethereum_balance(api_key, address)
    ether_balance = wei_to_ether(wei_balance)
    eth_to_usd_rate = get_eth_to_usd_rate()
    usd_balance = ether_balance * eth_to_usd_rate
    return usd_balance

def get_ethereum_transactions(address, startblock, endblock, page, offset, sort, api_key):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": startblock,
        "endblock": endblock,
        "page": page,
        "offset": offset,
        "sort": sort,
        "apikey": api_key
    }
    
    response = requests.get(url, params=params)
    return response.json()