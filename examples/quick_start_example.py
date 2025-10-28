#!/usr/bin/env python3
"""
Quick Start Example - Minimal NFT Vending Machine Setup

This is the simplest possible setup to get started quickly.
Perfect for testing and learning how the vending machine works.

Quick Start Steps:
1. Update the configuration variables below
2. Run: python3 examples/quick_start_example.py
3. The vending machine will start and process transactions

For production use, see the other examples in this directory.
"""

import os
import time
from cardano.wt.blockfrost import BlockfrostApi
from cardano.wt.cardano_cli import CardanoCli
from cardano.wt.mint import Mint
from cardano.wt.nft_vending_machine import NftVendingMachine
from cardano.wt.utxo import Balance
from cardano.wt.whitelist.no_whitelist import NoWhitelist


# ==========================================
# CONFIGURATION - Update these values!
# ==========================================

# Network
MAINNET = False  # Use True for production
BLOCKFROST_ID = "testnet-id"  # Your Blockfrost API key

# Addresses (create with cardano-cli or use pre-existing)
PAYMENT_ADDR = "addr_test1..."         # Where customers send ADA
PAYMENT_KEY = "/path/to/payment.skey"  # Signing key for payment address
PROFIT_ADDR = "addr_test1..."          # Where profits go

# Mint details
PRICE_ADA = 10                          # Price in ADA (will be converted to lovelace)
SCRIPT_FILE = "/path/to/policy.script" # Your minting policy script
SIGNING_KEY = "/path/to/mint.skey"     # Key to sign mint transactions

# Directories
METADATA_DIR = "nft_metadata/"         # Where your NFT JSON files are
OUTPUT_DIR = "vm_output/"              # Where vending machine will store data

# Optional settings
MAX_PER_TX = 5                         # Maximum NFTs per transaction
RANDOM_SELECTION = True                # Pick random NFTs (recommended)


def main():
    """Run the vending machine"""
    
    print("=" * 60)
    print("NFT VENDING MACHINE - QUICK START")
    print("=" * 60)
    print()
    
    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'in_proc'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'metadata'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'wl_consumed'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'txns'), exist_ok=True)
    
    print("Creating vending machine...")
    
    # Setup whitelist (none for this example)
    whitelist = NoWhitelist()
    
    # Setup prices
    price_lovelace = PRICE_ADA * 1_000_000
    prices = [Balance(price_lovelace, "LOVELACE")]
    
    # Setup mint
    mint = Mint(
        prices=prices,
        dev_fee=0,
        dev_addr=None,
        nfts_dir=METADATA_DIR,
        scripts=[SCRIPT_FILE],
        sign_keys=[SIGNING_KEY],
        whitelist=whitelist,
        bogo=None
    )
    
    # Setup Blockfrost API
    blockfrost_api = BlockfrostApi(BLOCKFROST_ID, mainnet=MAINNET)
    
    # Setup Cardano CLI wrapper (simplified for quickstart)
    cardano_cli = CardanoCli(protocol_params=None)
    
    # Create vending machine
    vm = NftVendingMachine(
        payment_addr=PAYMENT_ADDR,
        payment_sign_key=PAYMENT_KEY,
        profit_addr=PROFIT_ADDR,
        vend_randomly=RANDOM_SELECTION,
        single_vend_max=MAX_PER_TX,
        mint=mint,
        blockfrost_api=blockfrost_api,
        cardano_cli=cardano_cli,
        mainnet=MAINNET
    )
    
    print("Validating configuration...")
    try:
        vm.validate()
        print("✓ Configuration valid!")
        print()
        print(f"Configuration:")
        print(f"  Price: {PRICE_ADA} ADA per NFT")
        print(f"  Max NFTs per transaction: {MAX_PER_TX}")
        print(f"  Random selection: {RANDOM_SELECTION}")
        print(f"  Metadata directory: {METADATA_DIR}")
        print(f"  Network: {'Mainnet' if MAINNET else 'Testnet'}")
        print()
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        print()
        print("Common issues:")
        print("  - Check that all file paths are correct")
        print("  - Ensure signing keys exist")
        print("  - Verify addresses are valid for your network")
        print("  - Make sure metadata directory contains NFT JSON files")
        return
    
    print("Starting vending machine...")
    print("Press Ctrl+C to stop")
    print()
    
    already_completed = set()
    
    try:
        while True:
            vm.vend(OUTPUT_DIR, 'in_proc', 'metadata', already_completed)
            time.sleep(15)
    except KeyboardInterrupt:
        print()
        print("Vending machine stopped.")


if __name__ == "__main__":
    main()
