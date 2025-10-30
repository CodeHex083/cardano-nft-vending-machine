# Blockfrost Integration Guide

This document explains how the Cardano NFT Vending Machine uses [Blockfrost.io](https://blockfrost.io) for blockchain data retrieval and transaction submission. Understanding this integration is critical for third-party maintainers who need to troubleshoot issues or modify the vending machine behavior.

## Table of Contents

1. [Overview](#overview)
2. [Setup Guide](#setup-guide)
3. [API Endpoints Used](#api-endpoints-used)
4. [Rate Limiting and Retry Logic](#rate-limiting-and-retry-logic)
5. [Validation and Whitelist Handling](#validation-and-whitelist-handling)
6. [Network Support](#network-support)

## Overview

The vending machine relies on Blockfrost as its primary source of blockchain data. Blockfrost provides:
- **Transaction validation**: Verifying payment UTXOs and their origin
- **Chain state queries**: Retrieving addresses, UTXOs, assets, and protocol parameters
- **Transaction submission**: Broadcasting minted NFT transactions to the network
- **Whitelist validation**: Checking wallet signatures and asset ownership

The `BlockfrostApi` class (located in `src/cardano/wt/blockfrost.py`) encapsulates all interactions with the Blockfrost service.

## Setup Guide

### 1. Create a Blockfrost Account

1. Navigate to [Blockfrost.io](https://blockfrost.io) and sign up for an account
2. Create a new project for your intended network:
   - **Mainnet**: Production use with real ADA
   - **Preprod**: Test network (recommended for development)
   - **Preview**: Early-stage test network

### 2. Obtain Project ID

After creating a project, you'll receive a **Project ID** (also called API key). This is a long hexadecimal string that authenticates your API requests.

**Important Security Notes:**
- Store your Project ID securely
- Never commit Project IDs to version control
- Use environment variables or secure configuration files
- Different networks require separate Project IDs

### 3. Configure Rate Limits

Blockfrost enforces rate limits based on your account tier:

| Tier | Requests/Second | Burst Capacity |
|------|----------------|----------------|
| Free | 10 | 500 |
| Starter | 50 | 500 |
| Developer | 250 | 500 |
| Professional | Custom | Custom |

**Important**: The vending machine **does not actively enforce these limits**. You are responsible for:
1. Staying within your tier's limits (enforced by Blockfrost)
2. Monitoring for 429 rate limit errors
3. Upgrading your tier if you consistently hit limits

**Upgrading your tier** will increase throughput and reduce the likelihood of rate limit errors.

### 4. Initialize BlockfrostApi

In your code or configuration:

```python
from cardano.wt.blockfrost import BlockfrostApi

# For Mainnet
blockfrost_api = BlockfrostApi(
    project='your-mainnet-project-id',
    mainnet=True
)

# For Preprod (default)
blockfrost_api = BlockfrostApi(
    project='your-preprod-project-id',
    mainnet=False,
    preview=False
)

# For Preview
blockfrost_api = BlockfrostApi(
    project='your-preview-project-id',
    preview=True
)
```

### 5. Testing Your Configuration

Before running the vending machine, verify your Blockfrost connection works:

```python
# Test connection and retrieve protocol parameters
params = blockfrost_api.get_protocol_parameters()
print(f"Connected successfully! Current epoch parameters retrieved.")
```

## API Endpoints Used

The following table documents all Blockfrost API endpoints called by the vending machine:

| Method | Endpoint | Purpose | Called By |
|--------|----------|---------|-----------|
| `GET` | `/assets/policy/{policy_id}` | Retrieve all assets under a policy (paginated) | `get_assets()` |
| `GET` | `/assets/{asset_id}` | Get metadata for a specific asset | `get_asset()`, tests |
| `GET` | `/txs/{tx_hash}` | Get transaction details | `get_txn()`, tests |
| `GET` | `/txs/{tx_hash}/utxos` | Get transaction inputs/outputs | `get_tx_utxos()`, `get_inputs()`, `get_outputs()`, validation |
| `GET` | `/txs/{tx_hash}/metadata` | Get transaction metadata | `get_metadata()`, wallet whitelist validation |
| `GET` | `/addresses/{address}/utxos` | List all UTXOs at an address (paginated) | `get_utxos()`, payment monitoring |
| `GET` | `/epochs/latest/parameters` | Get current protocol parameters | `get_protocol_parameters()`, fee calculation |
| `POST` | `/tx/submit` | Submit signed transaction to network | `submit_txn()`, mint submission |

### Endpoint Usage Details

#### Transaction Validation (`/txs/{tx_hash}/utxos`)

Used extensively during the vending process:
- **Location**: `nft_vending_machine.py::__do_vend()`
- **Purpose**: Verify where payment UTXOs originated and extract sender addresses
- **Example**: When a user sends payment, the vending machine queries this endpoint to validate the transaction and identify the sender

```python
# In nft_vending_machine.py line 200
utxos = self.blockfrost_api.get_tx_utxos(mint_req.hash)
utxo_inputs = utxos['inputs']
input_addrs = set([utxo_input['address'] for utxo_input in utxo_inputs])
```

#### Address UTXO Monitoring (`/addresses/{address}/utxos`)

Used in the main vending loop:
- **Location**: `nft_vending_machine.py::vend()`
- **Purpose**: Continuously monitor the payment address for new UTXOs (mint requests)
- **Pagination**: Handles addresses with many UTXOs by fetching 100 at a time

```python
# In nft_vending_machine.py line 252
mint_reqs = self.blockfrost_api.get_utxos(self.payment_addr, exclusions)
```

#### Whitelist Validation (`/txs/{tx_hash}/metadata`)

Used for wallet-based whitelists:
- **Location**: `whitelist/wallet_whitelist.py::required_info()`
- **Purpose**: Retrieve CIP-8 signed messages proving whitelist eligibility
- **Critical**: Without this endpoint, wallet whitelist validation cannot function

```python
# In wallet_whitelist.py line 34
'metadata': blockfrost.get_metadata(mint_utxo.hash)
```

#### Asset Queries (`/assets/policy/{policy_id}`)

Used for asset-based whitelist initialization:
- **Location**: `scripts/initialize_whitelist.py`
- **Purpose**: Enumerate all assets under a policy to build whitelist files
- **Note**: Only called during whitelist setup, not during active vending

#### Transaction Submission (`/tx/submit`)

Used to broadcast minted transactions:
- **Location**: `nft_vending_machine.py::__do_vend()`
- **Purpose**: Submit the signed mint transaction to the Cardano network
- **Content-Type**: `application/cbor` (binary Cardano transaction format)

## Rate Limiting and Retry Logic

### Rate Limit Configuration

The vending machine defines rate limit constants for reference, but **does not actively enforce rate limiting**. The Blockfrost service itself enforces limits on their end:

```python
_API_CALLS_PER_SEC = 10    # Reference: Free tier limit (not enforced)
_BACKOFF_SEC = 10          # Wait time multiplier for retries
_MAX_GET_RETRIES = 9       # Maximum retries for GET requests
_MAX_POST_RETRIES = 2      # Maximum retries for POST requests
_UTXO_LIST_LIMIT = 100     # Pagination limit per request
```

**Note**: The code does not currently implement active rate limiting. If you exceed Blockfrost's limits (429 errors), you may need to:
- Upgrade your Blockfrost tier
- Reduce vending frequency (`WAIT_TIMEOUT` in main.py)
- Implement additional rate limiting in your code

### Retry Strategy

The `__call_with_retries()` method implements exponential backoff for HTTP errors:

1. **Initial Request**: Attempts API call immediately
2. **On HTTP Error**: If request fails (except 404), waits `retries * 10 seconds` before retrying
   - First retry: 10 seconds delay
   - Second retry: 20 seconds delay
   - Third retry: 30 seconds delay
   - ...
   - Maximum retries: 9 for GET requests, 2 for POST requests
3. **Success**: Returns JSON response immediately
4. **Failure After Max Retries**: Raises the HTTP exception (including 429 rate limit errors)

**Important Limitations**:
- **Rate Limit Errors (429)**: Not handled specially - they will retry but likely continue to fail until rate limit window expires
- **No Active Throttling**: The vending machine doesn't proactively throttle requests to stay under limits
- **Recommendation**: Monitor Blockfrost usage and consider implementing additional rate limiting if you encounter 429 errors frequently

### Handling 404 Not Found

Several endpoints gracefully handle 404 responses:
- `get_asset()`: Returns `None` if asset doesn't exist
- `get_txn()`: Returns `None` if transaction not found
- Paginated endpoints: Treat 404 as "no more pages"

### Error Scenarios

| Error Code | Handling | Impact |
|------------|----------|--------|
| 200-299 | Success, continue | Normal operation |
| 404 | Handled gracefully | May indicate missing data |
| 429 | Not explicitly handled | May cause vending to slow/fail |
| 500-599 | Retry with backoff | Temporary service issues |
| Other | Raise exception | Fatal error, investigate |

## Validation and Whitelist Handling

### Payment Validation Flow

1. **Monitor Payment Address**: `get_utxos()` polls for new UTXOs
2. **Verify Transaction**: `get_tx_utxos()` retrieves payment transaction details
3. **Extract Sender**: Input addresses identify who sent the payment
4. **Whitelist Check**: Whitelist implementation validates eligibility
5. **Process Mint**: If valid, mint NFTs and submit transaction

### Asset-Based Whitelist

- **Uses**: `get_tx_utxos()` to extract output UTXOs
- **Validation**: Checks if assets in payment outputs match whitelist files
- **No additional Blockfrost calls** during validation (uses transaction data already retrieved)

### Wallet-Based Whitelist

Requires additional Blockfrost calls:
- **Metadata Retrieval**: `get_metadata()` fetches CIP-8 signed message
- **Signature Verification**: Validates stake key signature
- **Address Matching**: Compares signed addresses with payment sender

This whitelist type is more Blockfrost-intensive and may hit rate limits faster.

### Whitelist Initialization

The `initialize_whitelist.py` script uses Blockfrost heavily:
- **Asset Mode**: `assets_policy()` to enumerate all policy assets
- **Wallet Mode**: `asset_addresses()` to resolve ADA handles to addresses

Run this script **once** before starting the vending machine to minimize runtime API usage.

## Network Support

The vending machine supports three Cardano networks via Blockfrost:

| Network | Base URL | Use Case |
|---------|----------|----------|
| Mainnet | `https://cardano-mainnet.blockfrost.io/api/v0` | Production |
| Preprod | `https://cardano-preprod.blockfrost.io/api/v0` | Testing (default) |
| Preview | `https://cardano-preview.blockfrost.io/api/v0` | Early testing |

**Important**: You need separate Blockfrost project IDs for each network. Mainnet projects typically require payment, while testnet projects are free.

### Network Selection

When initializing `BlockfrostApi`:

```python
# Mainnet
api = BlockfrostApi(project_id, mainnet=True)

# Preprod (default)
api = BlockfrostApi(project_id)  # or mainnet=False, preview=False

# Preview
api = BlockfrostApi(project_id, preview=True)
```

## Troubleshooting

### Common Issues

1. **Rate Limit Exceeded (429)**
   - **Solution**: Upgrade Blockfrost tier or reduce request frequency
   - **Check**: Monitor `_API_CALLS_PER_SEC` vs your tier limits

2. **Project ID Invalid (403)**
   - **Solution**: Verify Project ID is correct and matches network
   - **Check**: Ensure mainnet/preprod/preview project matches flag

3. **Transaction Not Found (404)**
   - **Normal**: May indicate transaction hasn't propagated yet
   - **Wait**: Blockfrost indexing can lag by a few seconds

4. **Connection Timeouts**
   - **Solution**: Check network connectivity and Blockfrost status page
   - **Mitigation**: Retry logic should handle temporary outages

### Monitoring API Usage

The vending machine prints API calls to stdout:
```
https://cardano-preprod.blockfrost.io/api/v0/txs/abc123.../utxos: (200)
```

Monitor these logs to:
- Track API call frequency
- Identify failing endpoints
- Debug rate limit issues

## Best Practices

1. **Separate Projects**: Use different Blockfrost projects for testing vs production
2. **Monitor Usage**: Keep an eye on Blockfrost dashboard for usage metrics
3. **Error Handling**: The vending machine retries automatically, but monitor logs for persistent failures
4. **Whitelist Efficiency**: Asset whitelists use fewer API calls than wallet whitelists
5. **Batch Operations**: The `initialize_whitelist.py` script batches operations to minimize API usage

## Additional Resources

- [Blockfrost API Documentation](https://docs.blockfrost.io/)
- [Blockfrost Rate Limits](https://docs.blockfrost.io/#section/Rate-limits)
- [Blockfrost Status Page](https://status.blockfrost.io/)
- [Cardano Testnets Documentation](https://docs.cardano.org/cardano-testnet/getting-started)

