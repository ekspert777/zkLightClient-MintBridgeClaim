# zkLightClient-MintBridgeClaim
Welcome to the zkLightClient-MintBridgeClaim project! This repository provides an interface to mint, bridge, and claim for zkLightClient NFT via [zkbridge](https://zkbridge.com/zknft).

## Getting Started
Before you begin, please make sure to obtain a Moralis API key. Moralis is a free-to-use service which you can sign up for [here](https://admin.moralis.io/register). Once you've gotten your key, you'll need to insert it into `data_storage.py` as follows: 

```python
MORALIS_API_KEY = 'YOUR_API_KEY'
```

## Bridging Assets
Currently, this solution supports bridging between Binance Smart Chain (BSC) and Polygon in both directions:

- BSC -> Polygon 
- Polygon -> BSC

## Private Key Setup
To initialize your wallet connections, add your private keys to `private_keys.txt`. Each key should be on its own line:

```txt
0x...
0x...
0x...
```

## Configuration
This script allows you to adjust the level of parallel processing by setting the `max_workers` parameter. Keep in mind that setting a very high number could lead to rate limiting from zkbridge, your rpc provider, or Moralis.

You'll also need to set `chain_from` and `chain_to` to specify the source and destination of the bridging operation. 

The final configuration call should look something like this:

```python
main(txt_path='private_keys.txt', max_workers=5, chain_from='BSC', chain_to='Polygon')
```

And voila! Your journey to potential wealth with Polyhedra starts here. With every NFT minted, a new hope for an airdrop shines brighter. Let's get minting and become the rockstars of the crypto world! (ChatGPT-4)

воркаем долбарики
