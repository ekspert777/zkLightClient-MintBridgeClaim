import datetime
from web3 import Web3
import time
import random
from data_storage import extra_wei_multiplier, public_rpc_dict, ankr_rpc_chain_name, polyhedra_nft_data
import requests
from moralis import evm_api


def get_time():

    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")

    return time_str


def get_nft_token_id_via_moralis(api_key, wallet_address, chain):
    try:

        api_key = api_key
        params = {
            "chain": ankr_rpc_chain_name[chain],
            "format": "decimal",
            "token_addresses": [
                polyhedra_nft_data[chain]['nft_contract_address']
                ],
                "media_items": False,
                "address": wallet_address,
                }
        result = evm_api.nft.get_wallet_nfts(
            api_key=api_key,
            params=params
            )
        return int(result['result'][0]['token_id'])

    except Exception as e:
        print(f'{get_time()} | get_nft_token_id_via_moralis | {wallet_address} | exception: {e}')
        return None


def start_web3(proxy=None, rpc=None, chain=None, public_rpc_dict=None, start_with_public=False, attempts=0):

    if attempts > 10:
        return False
    try:

        if proxy:
            proxies = {
                'http': proxy,
                'https': proxy
            }

            session = requests.Session()
            session.proxies = proxies

        if not rpc:
            if not chain:
                rpc = 'https://rpc.ankr.com/eth/'
            else:
                ankr_chain = ankr_rpc_chain_name[chain]
                rpc = f'https://rpc.ankr.com/{ankr_chain}/'

        if not public_rpc_dict:

            attempts = 0
            while True:

                if attempts > 2:
                    return False

                try:
                    if proxy:
                        web3 = Web3(Web3.HTTPProvider(rpc, session=session))
                    else:
                        web3 = Web3(Web3.HTTPProvider(rpc))

                    web3.eth.account.enable_unaudited_hdwallet_features()
                    connection_established = web3.is_connected()
                    if connection_established:
                        return web3
                    else:
                        attempts += 1
                        time.sleep(15)

                except Exception as e:
                    attempts += 1
                    time.sleep(15)

        else:
            if not start_with_public:
                try:
                    if proxy:
                        web3 = Web3(Web3.HTTPProvider(rpc, session=session))
                    else:
                        web3 = Web3(Web3.HTTPProvider(rpc))

                    web3.eth.account.enable_unaudited_hdwallet_features()
                    connection_established = web3.is_connected()
                    if connection_established:
                        return web3
                    else:
                        raise Exception

                except Exception as e:
                    random.shuffle(public_rpc_dict[chain])
                    for public_rpc in public_rpc_dict[chain]:
                        try:
                            if proxy:
                                web3 = Web3(Web3.HTTPProvider(public_rpc, session=session))
                            else:
                                web3 = Web3(Web3.HTTPProvider(public_rpc))

                            web3.eth.account.enable_unaudited_hdwallet_features()

                            connection_established = web3.is_connected()
                            if connection_established:
                                return web3

                        except Exception as e:
                            time.sleep(2)

                    return False
            else:
                random.shuffle(public_rpc_dict[chain])
                for public_rpc in public_rpc_dict[chain]:
                    try:
                        if proxy:
                            web3 = Web3(Web3.HTTPProvider(public_rpc, session=session))
                        else:
                            web3 = Web3(Web3.HTTPProvider(public_rpc))

                        web3.eth.account.enable_unaudited_hdwallet_features()
                        connection_established = web3.is_connected()
                        if connection_established:
                            return web3

                    except Exception as e:
                        time.sleep(2)

                raise Exception("ALL PUBLIC RPCs COULDN'T CONNECT")
    except Exception as e:
        print(f'{get_time()} | start_web3 exception: {e} | proxy: {proxy}')
        time.sleep(10)
        if attempts > 3:
            proxy = None
        start_web3(proxy=proxy, rpc=rpc, chain=chain, public_rpc_dict=public_rpc_dict,
                   start_with_public=start_with_public, attempts=attempts+1)


def get_gas_data(chain, proxy=None, bsc_gwei=None):

    for i in range(5):
        try:
            web3 = start_web3(proxy=proxy,
                              chain=chain, public_rpc_dict=public_rpc_dict, start_with_public=True)
            chain_id = web3.eth.chain_id
            base_fee = web3.eth.gas_price

            if chain_id in [1, 137, 42161, 43114]:
                if extra_wei_multiplier[chain_id]['maxFeePerGas']['type'] == 'static':
                    max_fee_per_gas = extra_wei_multiplier[chain_id]['maxFeePerGas']['value']
                elif extra_wei_multiplier[chain_id]['maxFeePerGas']['type'] == 'multiplier':
                    max_fee_per_gas = int(base_fee *
                                          extra_wei_multiplier[chain_id]['maxFeePerGas']['value'])
                else:
                    print(f"Unknown maxFeePerGas type"
                          f" {extra_wei_multiplier[chain_id]['maxFeePerGas']['type']} for chain {chain_id}")

                    return False

                if extra_wei_multiplier[chain_id]['maxPriorityFeePerGas']['type'] == 'static':
                    max_priority_fee_per_gas = extra_wei_multiplier[chain_id]['maxPriorityFeePerGas']['value']
                elif extra_wei_multiplier[chain_id]['maxPriorityFeePerGas']['type'] == 'multiplier':
                    max_priority_fee_per_gas = int(web3.eth.max_priority_fee *
                                                   extra_wei_multiplier[chain_id]['maxPriorityFeePerGas']['value'])
                else:
                    print(f"Unknown maxPriorityFeePerGas type"
                          f" {extra_wei_multiplier[chain_id]['maxPriorityFeePerGas']['type']} for chain {chain_id}")
                    return False

                gas_data = {'type': '0x2',
                            'maxFeePerGas': max_fee_per_gas,
                            'maxPriorityFeePerGas': max_priority_fee_per_gas,
                            'chainId': chain_id}

            elif chain_id in [10, 56, 250]:
                base_fee = web3.eth.gas_price
                if chain_id == 56:
                    if bsc_gwei:
                        base_fee = web3.to_wei(bsc_gwei, 'gwei')
                    else:
                        base_fee = web3.to_wei(3, 'gwei')
                else:
                    base_fee *= 1.2

                gas_data = {'gasPrice': int(base_fee),
                            'chainId': chain_id}
            else:
                print(f'UNKNOWN CHAIN ID | CHAIN: {chain} | CHAIN ID: {chain_id} | ADD TO GET_GAS_DATA FUNC')
                return False

            return gas_data

        except Exception as e:
            time.sleep(random.uniform(10, 20))
            print(f'{get_time()} | get_gas_data exception: {e}')


def sign_and_wait_for_tx_receipt(function_name, web3, transaction, private_key):
    signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    try:
        print(f'{get_time()} | {function_name} |'
              f' waiting for tx_receipt: {tx_hash.hex()}')
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    except Exception as e:
        print(f'{get_time()} | {function_name} |'
              f' waiting for tx_receipt FAILED | exception: {e}')

    return False


if __name__ == '__main__':
    print()