#!/usr/bin/env python3
"""
Full Integration Example - Complete NFT Vending Machine Setup

This example shows a complete, production-ready setup with:
- Multi-policy support
- Whitelist integration
- Developer fees
- BOGO deals
- Error handling and logging
- Configuration management

Use Case: Professional NFT drop with all features enabled
"""

import json
import os
import time
from datetime import datetime
from cardano.wt.bonuses.bogo import Bogo
from cardano.wt.blockfrost import BlockfrostApi
from cardano.wt.cardano_cli import CardanoCli
from cardano.wt.mint import Mint
from cardano.wt.nft_vending_machine import NftVendingMachine
from cardano.wt.utxo import Balance
from cardano.wt.whitelist.asset_whitelist import SingleUseWhitelist
from cardano.wt.whitelist.no_whitelist import NoWhitelist


class VendingMachineConfig:
    """
    Configuration management for vending machine
    """
    
    def __init__(self, config_file=None):
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()
    
    def _default_config(self):
        return {
            "network": {
                "mainnet": False,
                "preview": False
            },
            "blockfrost": {
                "project_id": "your-project-id"
            },
            "addresses": {
                "payment_address": "addr1...",
                "payment_signing_key": "/path/to/payment.skey",
                "profit_address": "addr1...",
                "dev_address": "addr1..."  # Optional
            },
            "mint": {
                "price_lovelace": 20000000,  # 20 ADA
                "policy_id": "LOVELACE",
                "script_path": "/path/to/policy.script",
                "signing_key": "/path/to/mint.skey"
            },
            "directories": {
                "metadata_directory": "/path/to/nft/metadata/",
                "output_directory": "/path/to/output/",
                "whitelist_directory": None  # Set to path if using whitelist
            },
            "vending": {
                "single_vend_max": 5,
                "vend_randomly": True
            },
            "fees": {
                "dev_fee_lovelace": 1000000,  # 1 ADA per NFT
                "enabled": True
            },
            "bogo": {
                "enabled": False,
                "threshold": 2,
                "bonus": 1
            },
            "whitelist": {
                "enabled": False,
                "type": "single_use"  # single_use, unlimited, wallet
            }
        }
    
    def get(self, *keys):
        """Get nested config value"""
        value = self.config
        for key in keys:
            value = value[key]
        return value
    
    def set(self, *keys, value):
        """Set nested config value"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def save(self, config_file):
        """Save configuration to file"""
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


def setup_directories(output_dir):
    """Create necessary directory structure"""
    dirs = [
        output_dir,
        os.path.join(output_dir, 'in_proc'),
        os.path.join(output_dir, 'metadata'),
        os.path.join(output_dir, 'wl_consumed'),
        os.path.join(output_dir, 'txns'),
        os.path.join(output_dir, 'logs')
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)


def initialize_whitelist(config):
    """Initialize whitelist based on configuration"""
    whitelist_type = config.get("whitelist", "type")
    
    if not config.get("whitelist", "enabled"):
        return NoWhitelist()
    
    whitelist_dir = config.get("directories", "whitelist_directory")
    consumed_dir = os.path.join(config.get("directories", "output_directory"), 'wl_consumed')
    
    if whitelist_type == "single_use":
        return SingleUseWhitelist(whitelist_dir, consumed_dir)
    elif whitelist_type == "unlimited":
        from cardano.wt.whitelist.asset_whitelist import UnlimitedWhitelist
        return UnlimitedWhitelist(whitelist_dir, consumed_dir)
    elif whitelist_type == "wallet":
        from cardano.wt.whitelist.wallet_whitelist import WalletWhitelist
        return WalletWhitelist(whitelist_dir, consumed_dir)
    else:
        return NoWhitelist()


def initialize_bogo(config):
    """Initialize BOGO deals if enabled"""
    if not config.get("bogo", "enabled"):
        return None
    
    threshold = config.get("bogo", "threshold")
    bonus = config.get("bogo", "bonus")
    return Bogo(threshold, bonus)


def log_event(message, log_file):
    """Log events to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())


def run_full_integration():
    """
    Run a complete vending machine integration
    """
    
    # Load configuration
    config = VendingMachineConfig()
    
    # Log file setup
    log_file = os.path.join(
        config.get("directories", "output_directory"),
        "logs",
        f"vending_machine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    try:
        log_event("Starting vending machine integration...", log_file)
        
        # Setup directories
        setup_directories(config.get("directories", "output_directory"))
        log_event("Created directory structure", log_file)
        
        # Initialize whitelist
        whitelist = initialize_whitelist(config)
        whitelist_desc = config.get("whitelist", "type") if config.get("whitelist", "enabled") else "none"
        log_event(f"Initialized whitelist: {whitelist_desc}", log_file)
        
        # Initialize BOGO
        bogo = initialize_bogo(config)
        bogo_desc = f"Buy {config.get('bogo', 'threshold')} Get {config.get('bogo', 'bonus')}" if bogo else "disabled"
        log_event(f"BOGO deals: {bogo_desc}", log_file)
        
        # Initialize prices
        prices = [Balance(
            config.get("mint", "price_lovelace"),
            config.get("mint", "policy_id")
        )]
        log_event(f"Set mint price: {config.get('mint', 'price_lovelace') / 1_000_000} ADA", log_file)
        
        # Initialize dev fee
        dev_fee = config.get("fees", "dev_fee_lovelace") if config.get("fees", "enabled") else 0
        dev_addr = config.get("addresses", "dev_address") if dev_fee else None
        if dev_fee:
            log_event(f"Developer fee: {dev_fee / 1_000_000} ADA per NFT", log_file)
        
        # Initialize mint
        mint = Mint(
            prices=prices,
            dev_fee=dev_fee,
            dev_addr=dev_addr,
            nfts_dir=config.get("directories", "metadata_directory"),
            scripts=[config.get("mint", "script_path")],
            sign_keys=[config.get("mint", "signing_key")],
            whitelist=whitelist,
            bogo=bogo
        )
        
        # Initialize Blockfrost
        blockfrost_api = BlockfrostApi(
            config.get("blockfrost", "project_id"),
            mainnet=config.get("network", "mainnet"),
            preview=config.get("network", "preview")
        )
        log_event("Initialized Blockfrost API", log_file)
        
        # Initialize Cardano CLI
        cardano_cli = CardanoCli(protocol_params=None)
        
        # Initialize vending machine
        vending_machine = NftVendingMachine(
            payment_addr=config.get("addresses", "payment_address"),
            payment_sign_key=config.get("addresses", "payment_signing_key"),
            profit_addr=config.get("addresses", "profit_address"),
            vend_randomly=config.get("vending", "vend_randomly"),
            single_vend_max=config.get("vending", "single_vend_max"),
            mint=mint,
            blockfrost_api=blockfrost_api,
            cardano_cli=cardano_cli,
            mainnet=config.get("network", "mainnet")
        )
        
        # Validate configuration
        log_event("Validating configuration...", log_file)
        vending_machine.validate()
        log_event("Validation successful!", log_file)
        log_event(f"Configuration:\n{vending_machine.as_json()}", log_file)
        
        # Run vending machine
        log_event("Starting vending machine loop...", log_file)
        already_completed = set()
        wait_timeout = 15
        
        while True:
            try:
                vending_machine.vend(
                    config.get("directories", "output_directory"),
                    'in_proc',
                    'metadata',
                    already_completed
                )
                time.sleep(wait_timeout)
            except KeyboardInterrupt:
                log_event("Vending machine stopped by user", log_file)
                break
            except Exception as e:
                log_event(f"Error in vending loop: {str(e)}", log_file)
                time.sleep(30)
    
    except Exception as e:
        log_event(f"Fatal error: {str(e)}", log_file)
        raise


if __name__ == "__main__":
    print("=" * 70)
    print("FULL INTEGRATION EXAMPLE - NFT VENDING MACHINE")
    print("=" * 70)
    print()
    print("This example demonstrates:")
    print("  ✓ Configuration management")
    print("  ✓ Whitelist integration")
    print("  ✓ Developer fees")
    print("  ✓ BOGO deals")
    print("  ✓ Error handling and logging")
    print()
    print("Update the VendingMachineConfig class or pass a config file")
    print("to customize your deployment.")
    print()
    
    run_full_integration()
