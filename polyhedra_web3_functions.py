from utils import start_web3, get_gas_data, sign_and_wait_for_tx_receipt, get_time
from data_storage import polyhedra_nft_data, public_rpc_dict
from web3.auto import w3
import time


def mint_nft(private_key, chain,
             gas_multiplier=1.0, bsc_gwei=1.1, attempts=0):
    try:
        if attempts > 5:
            return False
        start_with_public = False if chain == 'BSC' else True
        web3 = start_web3(chain=chain, public_rpc_dict=public_rpc_dict, start_with_public=start_with_public)
        account = web3.eth.account.from_key(private_key)
        wallet_address = account.address

        nft_contract_address = w3.to_checksum_address(polyhedra_nft_data[chain]['nft_contract_address'])
        nft_contract_abi = polyhedra_nft_data[chain]['nft_contract_abi']
        nft_contract = web3.eth.contract(address=nft_contract_address,
                                         abi=nft_contract_abi)

        tx_gas_data = get_gas_data(chain=chain, bsc_gwei=bsc_gwei)
        tx_gas_data['from'] = wallet_address
        tx_gas_data['nonce'] = web3.eth.get_transaction_count(wallet_address)
        transaction = nft_contract.functions.mint().build_transaction(tx_gas_data)
        transaction['gas'] = int(web3.eth.estimate_gas(transaction) * gas_multiplier)
        receipt = sign_and_wait_for_tx_receipt(function_name='mint_nft', web3=web3,
                                               transaction=transaction, private_key=private_key)
        if not receipt:  # tx didn't get to block because of low gas
            time.sleep(15)
            mint_nft(private_key, chain, gas_multiplier=gas_multiplier,
                     bsc_gwei=bsc_gwei+0.2, attempts=attempts+1)
        else:
            if receipt['status']:
                print(f'{get_time()} | mint_nft | {wallet_address} | minted successfully')
                return receipt
            else:  # failed tx with status 0
                if gas_multiplier > 1:
                    return False
                time.sleep(15)
                mint_nft(private_key, chain,
                         gas_multiplier=gas_multiplier+0.25, bsc_gwei=bsc_gwei, attempts=attempts+1)

    except Exception as e:
        if 'execution reverted: Each address may claim one NFT only. You have claimed already.' in str(e):
            print(f'{get_time()} | mint_nft | {wallet_address} | has already minted, continuing')
            return {'from': wallet_address, 'status': 1}

        print(f'{get_time()} | mint_nft | {wallet_address} | exception: {e}')
        time.sleep(15)
        return mint_nft(private_key, chain,
                        gas_multiplier=gas_multiplier+0.1, bsc_gwei=bsc_gwei, attempts=attempts+1)


def approve_nft(private_key, chain, nft_token_id,
                gas_multiplier=1.0, bsc_gwei=1.1, attempts=0):
    try:
        if attempts > 5:
            return False
        start_with_public = False if chain == 'BSC' else True
        web3 = start_web3(chain=chain, public_rpc_dict=public_rpc_dict, start_with_public=start_with_public)
        account = web3.eth.account.from_key(private_key)
        wallet_address = account.address

        nft_contract_address = w3.to_checksum_address(polyhedra_nft_data[chain]['nft_contract_address'])
        nft_contract_abi = polyhedra_nft_data[chain]['nft_contract_abi']
        nft_contract = web3.eth.contract(address=nft_contract_address,
                                         abi=nft_contract_abi)
        spender = polyhedra_nft_data[chain]['transfer_contract_address']

        tx_gas_data = get_gas_data(chain=chain, bsc_gwei=bsc_gwei)
        tx_gas_data['from'] = wallet_address
        tx_gas_data['nonce'] = web3.eth.get_transaction_count(wallet_address)

        transaction = nft_contract.functions.approve(spender, nft_token_id).build_transaction(tx_gas_data)
        transaction['gas'] = int(web3.eth.estimate_gas(transaction) * gas_multiplier)
        receipt = sign_and_wait_for_tx_receipt(function_name='approve_nft', web3=web3,
                                               transaction=transaction, private_key=private_key)
        if not receipt:  # tx didn't get to block because of low gas
            time.sleep(15)
            approve_nft(private_key, chain, nft_token_id, gas_multiplier=gas_multiplier,
                        bsc_gwei=bsc_gwei+0.2, attempts=attempts+1)
        else:
            if receipt['status']:
                print(f'{get_time()} | approve_nft | {wallet_address} | approved successfully')
                return receipt
            else:  # failed tx with status 0
                if gas_multiplier > 1:
                    return False
                time.sleep(15)
                approve_nft(private_key, chain, nft_token_id,
                            gas_multiplier=gas_multiplier+0.25, bsc_gwei=bsc_gwei, attempts=attempts+1)

    except Exception as e:
        print(f'{get_time()} | approve_nft | {wallet_address} | exception: {e}')
        time.sleep(15)
        return approve_nft(private_key, chain, nft_token_id,
                           gas_multiplier=gas_multiplier+0.1, bsc_gwei=bsc_gwei, attempts=attempts+1)


def bridge_nft(private_key, chain_from, chain_to, nft_token_id,
               gas_multiplier=1.0, bsc_gwei=1.1, attempts=0):
    try:
        if attempts > 5:
            return False
        start_with_public = False if chain_from == 'BSC' else True
        web3 = start_web3(chain=chain_from, public_rpc_dict=public_rpc_dict, start_with_public=start_with_public)
        account = web3.eth.account.from_key(private_key)
        wallet_address = account.address

        transfer_contract_address = w3.to_checksum_address(polyhedra_nft_data[chain_from]['transfer_contract_address'])
        transfer_contract_abi = polyhedra_nft_data[chain_from]['transfer_contract_abi']
        transfer_contract = web3.eth.contract(address=transfer_contract_address,
                                              abi=transfer_contract_abi)

        tx_gas_data = get_gas_data(chain=chain_from, bsc_gwei=bsc_gwei)
        tx_gas_data['from'] = wallet_address
        tx_gas_data['nonce'] = web3.eth.get_transaction_count(wallet_address)

        tx_values = {'BSC': w3.to_wei(0.001, 'ether'),
                     'Polygon': w3.to_wei(0.8, 'ether')}
        tx_gas_data['value'] = tx_values[chain_from]

        transaction = transfer_contract.functions.transferNFT(
            w3.to_checksum_address(polyhedra_nft_data[chain_from]['nft_contract_address']),
            nft_token_id,
            polyhedra_nft_data[chain_to]['polyhedra_chain_id'],
            '0x000000000000000000000000' + wallet_address[2:]
            ).build_transaction(tx_gas_data)
        transaction['gas'] = int(web3.eth.estimate_gas(transaction) * gas_multiplier)
        receipt = sign_and_wait_for_tx_receipt(function_name='bridge_nft', web3=web3,
                                               transaction=transaction, private_key=private_key)

        if not receipt:  # tx didn't get to block because of low gas
            time.sleep(15)
            bridge_nft(private_key, chain_from, chain_to, nft_token_id, gas_multiplier=gas_multiplier,
                       bsc_gwei=bsc_gwei+0.2, attempts=attempts+1)
        else:
            if receipt['status']:
                print(f'{get_time()} | bridge_nft | {wallet_address} | bridged successfully')
                return receipt
            else:  # failed tx with status 0
                if gas_multiplier > 1:
                    return False
                time.sleep(15)
                bridge_nft(private_key, chain_from, chain_to, nft_token_id,
                           gas_multiplier=gas_multiplier+0.25, bsc_gwei=bsc_gwei, attempts=attempts+1)

    except Exception as e:
        print(f'{get_time()} | bridge_nft | {wallet_address} | exception: {e}')
        time.sleep(15)
        return bridge_nft(private_key, chain_from, chain_to, nft_token_id,
                          gas_multiplier=gas_multiplier+0.1, bsc_gwei=bsc_gwei, attempts=attempts+1)


def claim_nft(private_key, chain, data_json,
              gas_multiplier=1.0, bsc_gwei=1.1, attempts=0):
    try:
        if attempts > 5:
            return False
        start_with_public = False if chain == 'BSC' else True
        web3 = start_web3(chain=chain, public_rpc_dict=public_rpc_dict, start_with_public=start_with_public)
        account = web3.eth.account.from_key(private_key)
        wallet_address = account.address

        transfer_contract_address = w3.to_checksum_address(polyhedra_nft_data[chain]['claim_contract_address'])
        transfer_contract_abi = polyhedra_nft_data[chain]['claim_contract_abi']
        transfer_contract = web3.eth.contract(address=transfer_contract_address,
                                              abi=transfer_contract_abi)

        tx_gas_data = get_gas_data(chain=chain, bsc_gwei=bsc_gwei)
        tx_gas_data['from'] = wallet_address
        tx_gas_data['nonce'] = web3.eth.get_transaction_count(wallet_address)

        transaction = transfer_contract.functions.validateTransactionProof(
            data_json['chain_id'],
            bytes.fromhex(data_json['block_hash'][2:]),
            data_json['proof_index'],
            bytes.fromhex(data_json['proof_blob'][2:])
            ).build_transaction(tx_gas_data)
        transaction['gas'] = int(web3.eth.estimate_gas(transaction) * gas_multiplier)
        receipt = sign_and_wait_for_tx_receipt(function_name='claim_nft', web3=web3,
                                               transaction=transaction, private_key=private_key)
        if not receipt:  # tx didn't get to block because of low gas
            time.sleep(15)
            claim_nft(private_key, chain, data_json, gas_multiplier=gas_multiplier,
                       bsc_gwei=bsc_gwei+0.2, attempts=attempts+1)
        else:
            if receipt['status']:
                print(f'{get_time()} | claim_nft | {wallet_address} | claimed successfully')
                return receipt
            else:  # failed tx with status 0
                if gas_multiplier > 1:
                    return False
                time.sleep(15)
                claim_nft(private_key, chain, data_json,
                          gas_multiplier=gas_multiplier+0.25, bsc_gwei=bsc_gwei, attempts=attempts+1)

    except Exception as e:
        print(f'{get_time()} | claim_nft | {wallet_address} | exception: {e}')
        time.sleep(15)
        return claim_nft(private_key, chain, data_json,
                         gas_multiplier=gas_multiplier+0.1, bsc_gwei=bsc_gwei, attempts=attempts+1)


if __name__ == '__main__':
    print()
