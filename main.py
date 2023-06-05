from polyhedra_requests import create_order_request, generate_proof_blob, claim_order_request
from utils import get_time, get_nft_token_id_via_moralis
from polyhedra_web3_functions import mint_nft, approve_nft, bridge_nft, claim_nft
from data_storage import MORALIS_API_KEY
import time
from concurrent.futures import ThreadPoolExecutor


def process_wallet(private_key, chain_from, chain_to):

    try:
        mint_tx = mint_nft(private_key=private_key, chain=chain_from)

        if not mint_tx:
            return False
        elif not mint_tx['status']:
            return False
        else:
            for i in range(15):
                time.sleep(10)
                nft_id = get_nft_token_id_via_moralis(api_key=MORALIS_API_KEY, wallet_address=mint_tx['from'],
                                                      chain=chain_from)
                if nft_id:
                    break

            if not nft_id:
                return False

        approve_tx = approve_nft(private_key=private_key, chain=chain_from, nft_token_id=nft_id)
        if not approve_tx:
            return False
        elif not approve_tx['status']:
            return False

        bridge_tx = bridge_nft(private_key=private_key, chain_from=chain_from, chain_to=chain_to,
                               nft_token_id=nft_id)
        if not bridge_tx:
            return False
        elif not bridge_tx['status']:
            return False

        create_order_id = create_order_request(wallet_address=mint_tx['from'], chain_from=chain_from, chain_to=chain_to,
                                               tx_hash=bridge_tx['transactionHash'].hex(), token_id=nft_id)
        if not create_order_id:
            return False

        response_json = generate_proof_blob(tx_hash=bridge_tx['transactionHash'].hex(), chain_from=chain_from)
        if not response_json:
            return False

        claim_tx = claim_nft(private_key=private_key, chain=chain_to, data_json=response_json)
        if not claim_tx:
            return False
        elif not claim_tx['status']:
            return False

        claim_post_request = claim_order_request(claim_hash=claim_tx['transactionHash'].hex(),
                                                 create_order_id=create_order_id)

        return claim_post_request

    except Exception as e:
        print(f'{get_time()} | main | exception: {e}')


def main(txt_path, max_workers, chain_from, chain_to):
    try:
        with open(txt_path, 'r') as f:
            private_keys = [row.strip() for row in f]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for private_key in private_keys:
                future = executor.submit(process_wallet, private_key, chain_from, chain_to)
                futures.append(future)

    except Exception as e:
        print(f'{get_time()} | main | exception: {e}')


if __name__ == '__main__':
    main(txt_path='private_keys.txt', max_workers=5, chain_from='BSC', chain_to='Polygon')


