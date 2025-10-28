# Example Integrations

This folder contains example implementations of the Cardano NFT Vending Machine demonstrating different use cases and configurations.

## Example Categories

### 🚀 Quick Start
- **Quick Start** (`quick_start_example.py`) - **Start here!** Minimal setup to get running fast

### 🎯 Basic Use Cases
- **Single Mint** (`single_mint_example.py`) - Simple vending machine without whitelist
- **Whitelist Integration** (`whitelist_example.py`) - Using asset-based or wallet-based whitelists
- **Profit Split** (`profit_split_example.py`) - Implementing profit splits and developer fees
- **Full Integration** (`full_integration_example.py`) - Complete setup with all features

### 📚 How to Use

Each example demonstrates:
- Setting up the necessary components
- Configuring mint parameters
- Initializing the vending machine
- Running the vend loop

1. **New users**: Start with `quick_start_example.py`
2. Choose an example that matches your needs
3. Update the configuration parameters at the top of the file
4. Run the example to see it in action

## 🤝 Contributing Your Integration

We encourage you to submit PRs with your own use cases!

### How to Submit
1. Create a new file in this directory (e.g., `your_integration.py`)
2. Follow the naming pattern: `[category]_example.py`
3. Include clear comments explaining your use case
4. Add a brief description in this README
5. Submit a PR with your integration

### Example Structure

Your example should include:
- Descriptive comments
- Configuration variables at the top
- Clear setup and initialization
- Proper error handling
- Documentation on what it demonstrates

### Integration Ideas We'd Love to See

- **Multi-policy Mints** - Managing multiple NFT policies in one mint
- **Native Token Payments** - Accepting custom tokens as payment
- **Presale/Public Sale** - Different phases of minting
- **Automated Airdrops** - Batch distribution to holders
- **Custom Rebates** - Advanced pricing strategies
- **Event-driven Integrations** - Webhook triggers for external events
- **Multi-wallet Operations** - Automatic profit splitting across wallets
- **Raindrop Distribution** - Random distribution from a collection
- **Dutch Auction** - Decreasing price over time
- **Whitelist Marketplace** - Transferable whitelist spots

### Submission Checklist

Before submitting your example:

- [ ] Code is well-commented and easy to understand
- [ ] Configuration variables are clearly documented
- [ ] Example includes error handling
- [ ] README is updated with your example
- [ ] Example follows the naming convention
- [ ] All sensitive paths use placeholders (`/path/to/`)
- [ ] Example works on testnet (include network flag)

## 📖 Additional Resources

- [Main README](../README.md) - Getting started with the library
- [API Documentation](https://thaddeusdiamond.github.io/cardano-nft-vending-machine/cardano/) - Full API reference
- [Script Examples](../scripts/) - Utility scripts for operations
- [Test Suite](../tests/) - See how the library is tested

## 🎓 Learning Path

1. **Start Here**: `quick_start_example.py` - Get something running
2. **Learn Basics**: `single_mint_example.py` - Understand core concepts
3. **Add Features**: `whitelist_example.py` - Implement access control
4. **Advanced**: `profit_split_example.py` - Add fees and bonuses
5. **Production**: `full_integration_example.py` - Complete setup with best practices

---

**⚠️ Important**: All examples are for demonstration purposes. Always test thoroughly on testnets before mainnet deployment. Never commit signing keys or sensitive credentials!
