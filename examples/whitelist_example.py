#!/usr/bin/env python3
"""
Whitelist Integration Example - NFT Vending Machine with Whitelist

This example demonstrates how to run a whitelisted NFT drop.
Supports three whitelist types:
1. Single-use asset whitelist - One NFT per asset used
2. Unlimited asset whitelist - Unlimited NFTs per asset
3. Wallet whitelist - Based on wallet addresses

Configuration:
- Whitelist-enforced mint
- Presale functionality
- Asset-based or wallet-based access

Use Case: Presale with whitelist access
"""

import os
import time
from cardano.wt.blockfrost import BlockfrostApi
from cardano.wt.cardano_cli import CardanoCli
from cardano.wt.mint import Mint
from cardano.wt.nft_vending_machine import NftVendingMachine
from cardano.wt.utxo import Balance
from cardano.wt.whitelist.asset_whitelist import SingleUseWhitelist, UnlimitedWhitelist
from cardano.wt.whitelist.wallet_whitelist import WalletWhitelist


def run_asset_whitelist_example():
    """
    Example using single-use asset whitelist
    Each whitelisted asset can mint up to N NFTs
    """
    
    # ==========================================
    # CONFIGURATION
    # ==========================================
    
    MAINNET = False
    PREVIEW = False
    BLOCKFROST_PROJECT_ID = "your-blockfrost-project-id"
    
    PAYMENT_ADDRESS = "addr1..."
    PAYMENT_SIGNING_KEY = "/path/to/payment.skey"
    PROFIT_ADDRESS = "addr1..."
    
    MINT_PRICE_LOVELACE = 15000000  # 15 ADA for presale
    MINT_SCRIPT_PATH = "/path/to/policy.script"
    MINT_SIGNING_KEY = "/path/to/mint.skey"
    
    METADATA_DIRECTORY = "/path/to/nft/metadata/"
    OUTPUT_DIRECTORY = "/path/to/vending/machine/output/"
    WHITELIST_DIRECTORY = "/path/to/whitelist/assets/"
    
    SINGLE_VEND_MAX = 3
    VEND_RANDOMLY = True
    
    # ==========================================
    # INITIALIZATION
    # ==========================================
    
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    consumed_dir = os.path.join(OUTPUT_DIRECTORY, 'wl_consumed')
    os.makedirs(consumed_dir, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'in_proc'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'metadata'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'txns'), exist_ok=True)
    
    # Single-use whitelist: each asset can mint up to 1 NFT
    whitelist = SingleUseWhitelist(WHITELIST_DIRECTORY, consumed_dir)
    
    # Alternative: Unlimited whitelist for VIP access
    # whitelist = UnlimitedWhitelist(WHITELIST_DIRECTORY, consumed_dir)
    
    prices = [Balance(MINT_PRICE_LOVELACE, "LOVELACE")]
    
    mint = Mint(
        prices=prices,
        dev_fee=0,
        dev_addr=None,
        nfts_dir=METADATA_DIRECTORY,
        scripts=[MINT_SCRIPT_PATH],
        sign_keys=[MINT_SIGNING_KEY],
        whitelist=whitelist,
        bogo=None
    )
    
    blockfrost_api = BlockfrostApi(BLOCKFROST_PROJECT_ID, mainnet=MAINNET, preview=PREVIEW)
    cardano_cli = CardanoCli(protocol_params=None)
    
    vending_machine = NftVendingMachine(
        payment_addr=PAYMENT_ADDRESS,
        payment_sign_key=PAYMENT_SIGNING_KEY,
        profit_addr=PROFIT_ADDRESS,
        vend_randomly=VEND_RANDOMLY,
        single_vend_max=SINGLE_VEND_MAX,
        mint=mint,
        blockfrost_api=blockfrost_api,
        cardano_cli=cardano_cli,
        mainnet=MAINNET
    )
    
    # Validate
    print("Validating whitelist vending machine...")
    vending_machine.validate()
    print("Validation successful!")
    print(f"\nVending machine config:\n{vending_machine.as_json()}")
    
    # Run
    print("\nStarting whitelisted vending machine...")
    already_completed = set()
    
    try:
        while True:
            vending_machine.vend(OUTPUT_DIRECTORY, 'in_proc', 'metadata', already_completed)
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nVending machine stopped")


def run_wallet_whitelist_example():
    """
    Example using wallet-based whitelist
    Each whitelisted wallet can mint up to N NFTs
    """
    
    # ==========================================
    # CONFIGURATION
    # ==========================================
    
    MAINNET = False
    BLOCKFROST_PROJECT_ID = "your-blockfrost-project-id"
    
    PAYMENT_ADDRESS = "addr1..."
    PAYMENT_SIGNING_KEY = "/path/to/payment.skey"
    PROFIT_ADDRESS = "addr1..."
    
    MINT_PRICE_LOVELACE = 20000000  # 20 ADA
    MINT_SCRIPT_PATH = "/path/to/policy.script"
    MINT_SIGNING_KEY = "/path/to/mint.skey"
    
    METADATA_DIRECTORY = "/path/to/nft/metadata/"
    OUTPUT_DIRECTORY = "/path/to/vending/machine/output/"
    WHITELIST_DIRECTORY = "/path/to/wallet/whitelist/"
    
    SINGLE_VEND_MAX = 2
    
    # ==========================================
    # INITIALIZATION
    # ==========================================
    
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    consumed_dir = os.path.join(OUTPUT_DIRECTORY, 'wl_consumed')
    os.makedirs(consumed_dir, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'in_proc'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'metadata'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'txns'), exist_ok=True)
    
    # Wallet whitelist: each wallet can mint up to 2 NFTs
    whitelist = WalletWhitelist(WHITELIST_DIRECTORY, consumed_dir)
    
    prices = [Balance(MINT_PRICE_LOVELACE, "LOVELACE")]
    
    mint = Mint(
        prices=prices,
        dev_fee=0,
        dev_addr=None,
        nfts_dir=METADATA_DIRECTORY,
        scripts=[MINT_SCRIPT_PATH],
        sign_keys=[MINT_SIGNING_KEY],
        whitelist=whitelist,
        bogo=None
    )
    
    blockfrost_api = BlockfrostApi(BLOCKFROST_PROJECT_ID, mainnet=MAINNET)
    cardano_cli = CardanoCli(protocol_params=None)
    
    vending_machine = NftVendingMachine(
        payment_addr=PAYMENT_ADDRESS,
        payment_sign_key=PAYMENT_SIGNING_KEY,
        profit_addr=PROFIT_ADDRESS,
        vend_randomly=True,
        single_vend_max=SINGLE_VEND_MAX,
        mint=mint,
        blockfrost_api=blockfrost_api,
        cardano_cli=cardano_cli,
        mainnet=MAINNET
    )
    
    # Validate and run
    print("Validating wallet whitelist vending machine...")
    vending_machine.validate()
    print("Validation successful!")
    
    print("\nStarting wallet-whitelisted vending machine...")
    already_completed = set()
    
    try:
        while True:
            vending_machine.vend(OUTPUT_DIRECTORY, 'in_proc', 'metadata', already_completed)
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nVending machine stopped")


if __name__ == "__main__":
    # Run asset-based whitelist example
    print("=" * 60)
    print("ASSET WHITELIST EXAMPLE")
    print("=" * 60)
    run_asset_whitelist_example()
    
    # Uncomment to run wallet-based whitelist example instead:
    # print("\n" + "=" * 60)
    # print("WALLET WHITELIST EXAMPLE")
    # print("=" * 60)
    # run_wallet_whitelist_example()
