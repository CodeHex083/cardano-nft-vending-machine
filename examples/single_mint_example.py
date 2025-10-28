#!/usr/bin/env python3
"""
Single Mint Example - Basic NFT Vending Machine

This example demonstrates a simple NFT vending machine setup without whitelist.
Perfect for public mints where anyone can purchase NFTs.

Configuration:
- No whitelist required
- Single payment address
- Direct profit to creator
- Random mint selection

Use Case: Public NFT drop with fixed price
"""

import os
import time
from cardano.wt.blockfrost import BlockfrostApi
from cardano.wt.cardano_cli import CardanoCli
from cardano.wt.mint import Mint
from cardano.wt.nft_vending_machine import NftVendingMachine
from cardano.wt.utxo import Balance
from cardano.wt.whitelist.no_whitelist import NoWhitelist


def run_single_mint_example():
    """
    Initialize and run a single-mint vending machine
    """
    
    # ==========================================
    # CONFIGURATION - Update these values
    # ==========================================
    
    # Network configuration
    MAINNET = False  # Set to True for production
    PREVIEW = False   # Set to True for preview network
    
    # Blockfrost API configuration
    BLOCKFROST_PROJECT_ID = "your-blockfrost-project-id"
    
    # Address configuration
    PAYMENT_ADDRESS = "addr1..."        # Where customers send payments
    PAYMENT_SIGNING_KEY = "/path/to/payment.skey"
    PROFIT_ADDRESS = "addr1..."         # Where profits are collected
    
    # Mint configuration
    MINT_PRICE_LOVELACE = 10000000      # 10 ADA (in lovelace)
    MINT_POLICY_ID = "LOVELACE"        # Using ADA (lovelace)
    
    # Script and key configuration
    MINT_SCRIPT_PATH = "/path/to/policy.script"
    MINT_SIGNING_KEY = "/path/to/mint.skey"
    
    # Directory configuration
    METADATA_DIRECTORY = "/path/to/nft/metadata/"
    OUTPUT_DIRECTORY = "/path/to/vending/machine/output/"
    
    # Vending configuration
    SINGLE_VEND_MAX = 5                 # Maximum NFTs per transaction
    VEND_RANDOMLY = True                # Random mint selection
    
    # ==========================================
    # INITIALIZATION
    # ==========================================
    
    # Create necessary directories
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'in_proc'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'metadata'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'wl_consumed'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'txns'), exist_ok=True)
    
    # Initialize whitelist (no whitelist for public mint)
    whitelist = NoWhitelist()
    
    # Initialize mint prices
    prices = [Balance(MINT_PRICE_LOVELACE, MINT_POLICY_ID)]
    
    # Initialize mint object
    mint = Mint(
        prices=prices,
        dev_fee=0,                      # No developer fee
        dev_addr=None,                  # No dev address needed
        nfts_dir=METADATA_DIRECTORY,
        scripts=[MINT_SCRIPT_PATH],
        sign_keys=[MINT_SIGNING_KEY],
        whitelist=whitelist,
        bogo=None                       # No BOGO deals
    )
    
    # Initialize Blockfrost API
    blockfrost_api = BlockfrostApi(
        BLOCKFROST_PROJECT_ID,
        mainnet=MAINNET,
        preview=PREVIEW
    )
    
    # Get protocol parameters
    protocol_params = blockfrost_api.get_protocol_parameters()
    
    # Initialize Cardano CLI wrapper
    # Note: In a real setup, you'd need to convert protocol params
    cardano_cli = CardanoCli(protocol_params=None)
    
    # Initialize vending machine
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
    
    # Validate configuration
    print("Validating vending machine configuration...")
    vending_machine.validate()
    print("Validation successful!")
    print(f"Vending machine configuration:\n{vending_machine.as_json()}")
    
    # ==========================================
    # RUN THE VENDING MACHINE
    # ==========================================
    
    print("\nStarting vending machine...")
    print("Press Ctrl+C to stop\n")
    
    already_completed = set()
    wait_timeout = 15  # seconds
    
    try:
        while True:
            vending_machine.vend(
                OUTPUT_DIRECTORY,
                'in_proc',
                'metadata',
                already_completed
            )
            time.sleep(wait_timeout)
    except KeyboardInterrupt:
        print("\nVending machine stopped by user")


if __name__ == "__main__":
    run_single_mint_example()
