#!/usr/bin/env python3
"""
Profit Split Example - NFT Vending Machine with Developer Fees

This example demonstrates profit splitting features:
- Developer fee distribution
- Multiple profit recipients
- BOGO (Buy One Get One) deals
- Profit tracking and reporting

Configuration:
- Developer fee collection
- Automated profit distribution
- Optional bonus NFTs

Use Case: Project with artist fees, marketplace fees, or bonus NFTs
"""

import os
import time
from cardano.wt.bonuses.bogo import Bogo
from cardano.wt.blockfrost import BlockfrostApi
from cardano.wt.cardano_cli import CardanoCli
from cardano.wt.mint import Mint
from cardano.wt.nft_vending_machine import NftVendingMachine
from cardano.wt.utxo import Balance
from cardano.wt.whitelist.no_whitelist import NoWhitelist


def run_profit_split_example():
    """
    Example with developer fee and BOGO deals
    """
    
    # ==========================================
    # CONFIGURATION
    # ==========================================
    
    MAINNET = False
    BLOCKFROST_PROJECT_ID = "your-blockfrost-project-id"
    
    # Payment configuration
    PAYMENT_ADDRESS = "addr1..."           # Where customers send payments
    PAYMENT_SIGNING_KEY = "/path/to/payment.skey"
    PROFIT_ADDRESS = "addr1..."            # Creator's profit address
    
    # Developer/marketplace configuration
    DEV_FEE_LOVELACE = 1000000             # 1 ADA per NFT to developer
    DEV_ADDRESS = "addr1..."                # Developer/marketplace address
    
    # Mint configuration
    MINT_PRICE_LOVELACE = 20000000         # 20 ADA per NFT
    MINT_SCRIPT_PATH = "/path/to/policy.script"
    MINT_SIGNING_KEY = "/path/to/mint.skey"
    
    # Directory configuration
    METADATA_DIRECTORY = "/path/to/nft/metadata/"
    OUTPUT_DIRECTORY = "/path/to/vending/machine/output/"
    
    # Vending configuration
    SINGLE_VEND_MAX = 5
    VEND_RANDOMLY = True
    
    # BOGO configuration
    # Buy 2, get 1 free (threshold=2, bonus=1)
    BOGO_THRESHOLD = 2
    BOGO_BONUS = 1
    
    # ==========================================
    # INITIALIZATION
    # ==========================================
    
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'in_proc'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'metadata'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'wl_consumed'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, 'txns'), exist_ok=True)
    
    # No whitelist (public mint with BOGO)
    whitelist = NoWhitelist()
    
    # Initialize BOGO bonus system
    bogo = Bogo(BOGO_THRESHOLD, BOGO_BONUS)
    
    prices = [Balance(MINT_PRICE_LOVELACE, "LOVELACE")]
    
    # Initialize mint with dev fee and BOGO
    mint = Mint(
        prices=prices,
        dev_fee=DEV_FEE_LOVELACE,
        dev_addr=DEV_ADDRESS,
        nfts_dir=METADATA_DIRECTORY,
        scripts=[MINT_SCRIPT_PATH],
        sign_keys=[MINT_SIGNING_KEY],
        whitelist=whitelist,
        bogo=bogo                          # Enable BOGO deals
    )
    
    blockfrost_api = BlockfrostApi(BLOCKFROST_PROJECT_ID, mainnet=MAINNET)
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
    print("Validating profit split vending machine...")
    vending_machine.validate()
    print("Validation successful!")
    print(f"\nConfiguration:")
    print(f"  Mint Price: {MINT_PRICE_LOVELACE / 1_000_000} ADA")
    print(f"  Developer Fee: {DEV_FEE_LOVELACE / 1_000_000} ADA per NFT")
    print(f"  BOGO Deal: Buy {BOGO_THRESHOLD}, Get {BOGO_BONUS} free")
    print(f"  Max NFTs per transaction: {SINGLE_VEND_MAX}")
    
    # Run
    print("\nStarting profit-split vending machine with BOGO deals...")
    print("Example transaction flow:")
    print("  - Customer buys 2 NFTs (40 ADA)")
    print("  - Customer receives 3 NFTs (1 bonus)")
    print("  - Creator receives: 19 ADA (less 1 ADA dev fee)")
    print("  - Developer receives: 2 ADA (1 ADA per NFT)")
    print()
    
    already_completed = set()
    
    try:
        while True:
            vending_machine.vend(OUTPUT_DIRECTORY, 'in_proc', 'metadata', already_completed)
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nVending machine stopped")


def run_multi_profit_example():
    """
    Advanced example: Multiple profit recipients
    Note: This is a conceptual example showing how you could extend the system
    """
    
    print("=" * 60)
    print("ADVANCED PROFIT SPLIT CONCEPT")
    print("=" * 60)
    print("""
    To implement multiple profit recipients, you would need to:
    
    1. Modify the NftVendingMachine class to accept multiple profit addresses
    2. Update the pricing breakdown logic to split profits across recipients
    3. Implement percentage-based or fixed-amount splits
    4. Handle balance calculations for each recipient
    
    Example splits:
    - Artist: 70% of profit
    - Marketplace: 20% of profit
    - DAO Treasury: 10% of profit
    
    This requires custom modifications to the vending machine code.
    See main.py and nft_vending_machine.py for implementation details.
    """)


if __name__ == "__main__":
    # Run basic profit split with BOGO
    run_profit_split_example()
    
    # Uncomment to see advanced concepts:
    # run_multi_profit_example()
