import requests
from utils import get_time
from data_storage import polyhedra_nft_data, chain_ids


def create_order_request(wallet_address, chain_from, chain_to, tx_hash, token_id, proxy=None):
    """

    :return: id for a future claim order request
    """
    try:
        json_data = {
            'from': wallet_address,
            'to': wallet_address,
            'sourceChainId': chain_ids[chain_from],
            'targetChainId': chain_ids[chain_to],
            'txHash': tx_hash,
            'contracts': [
                {
                    'contractAddress': polyhedra_nft_data[chain_from]['nft_contract_address'],
                    'tokenId': token_id,
                },
            ],
        }

        if proxy:
            proxies = {'http': proxy, 'https': proxy}
            response = requests.post('https://api.zkbridge.com/api/bridge/createOrder', json=json_data, proxies=proxies)
        else:
            response = requests.post('https://api.zkbridge.com/api/bridge/createOrder', json=json_data)

        if response.status_code == 200:
            needed_id = response.json()['id']
            return needed_id
        else:
            print(f'{get_time()} | wallet: {wallet_address} | create_order_request status code: {response.status_code}')
            return False

    except Exception as e:
        print(f'{get_time()} | wallet: {wallet_address} | create_order_request exception: {e}')
        return False


def generate_proof_blob(tx_hash, chain_from, proxy=None):
    """

    :return: response json for a following claim in the destination chain
    """
    for i in range(10):
        try:
            json_data = {
                'tx_hash': tx_hash,
                'chain_id': polyhedra_nft_data[chain_from]['polyhedra_chain_id'],
                'testnet': False,
            }

            if proxy:
                proxies = {'http': proxy, 'https': proxy}
                response = requests.post(
                    'https://api.zkbridge.com/api/v2/receipt_proof/generate', json=json_data, proxies=proxies
                )
            else:
                response = requests.post(
                    'https://api.zkbridge.com/api/v2/receipt_proof/generate', json=json_data
                )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            print(f'{get_time()} | tx hash: {tx_hash} | generate_proof_blob exception: {e}')
            return False

    print(f'{get_time()} | tx hash: {tx_hash} | failed to generate proof blob in 10 tries')
    return False


def claim_order_request(claim_hash, create_order_id, proxy=None):
    """
    send a post request containing hash of claim tx to zkbridge
    :return: status code of post request
    """
    try:
        json_data = {
            'claimHash': claim_hash,
            'id': create_order_id,
        }

        if proxy:
            proxies = {'http': proxy, 'https': proxy}
            response = requests.post('https://api.zkbridge.com/api/bridge/claimOrder', json=json_data, proxies=proxies)
        else:
            response = requests.post('https://api.zkbridge.com/api/bridge/claimOrder', json=json_data)

        if response.status_code == 200:
            print(f'{get_time()} | claim hash: {claim_hash} | finished successfully')
            return True
        else:
            print(f'{get_time()} | claim hash: {claim_hash} | claim_order_request status code: {response.status_code}')
            return False

    except Exception as e:
        print(f'{get_time()} | claim hash: {claim_hash} | claim_order_request exception: {e}')
        return False


if __name__ == '__main__':
    print()