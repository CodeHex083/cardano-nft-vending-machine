#!/usr/bin/env bash
set -euo pipefail

# Build command dynamically from env vars to invoke main.py
CMD_ARGS=( )

# Required core args (user should provide via env)
if [[ -n "${PAYMENT_ADDR:-}" ]]; then CMD_ARGS+=( "--payment-addr" "$PAYMENT_ADDR" ); fi
if [[ -n "${PAYMENT_SIGN_KEY_PATH:-}" ]]; then CMD_ARGS+=( "--payment-sign-key" "$PAYMENT_SIGN_KEY_PATH" ); fi
if [[ -n "${PROFIT_ADDR:-}" ]]; then CMD_ARGS+=( "--profit-addr" "$PROFIT_ADDR" ); fi

# Mint prices: support semicolon-separated pairs: "<PRICE> <POLICY>; <PRICE> <POLICY>"
if [[ -n "${MINT_PRICES:-}" ]]; then
  IFS=';' read -ra PAIRS <<< "$MINT_PRICES"
  for pair in "${PAIRS[@]}"; do
    pair_trimmed=$(echo "$pair" | xargs)
    if [[ -n "$pair_trimmed" ]]; then
      price=$(echo "$pair_trimmed" | awk '{print $1}')
      policy=$(echo "$pair_trimmed" | awk '{print $2}')
      CMD_ARGS+=( "--mint-price" "$price" "$policy" )
    fi
  done
fi

# Alternatively support single pair ENV vars
if [[ -n "${MINT_PRICE:-}" && -n "${MINT_POLICY_ID:-}" ]]; then
  CMD_ARGS+=( "--mint-price" "$MINT_PRICE" "$MINT_POLICY_ID" )
fi

# Mint scripts and keys: support comma-separated lists
if [[ -n "${MINT_SCRIPT_PATHS:-}" ]]; then
  IFS=',' read -ra SCRIPTS <<< "$MINT_SCRIPT_PATHS"
  for s in "${SCRIPTS[@]}"; do CMD_ARGS+=( "--mint-script" "$(echo "$s" | xargs)" ); done
fi
if [[ -n "${MINT_SIGN_KEY_PATHS:-}" ]]; then
  IFS=',' read -ra KEYS <<< "$MINT_SIGN_KEY_PATHS"
  for k in "${KEYS[@]}"; do CMD_ARGS+=( "--mint-sign-key" "$(echo "$k" | xargs)" ); done
fi

if [[ -n "${METADATA_DIR:-}" ]]; then CMD_ARGS+=( "--metadata-dir" "$METADATA_DIR" ); fi
if [[ -n "${OUTPUT_DIR:-}" ]]; then CMD_ARGS+=( "--output-dir" "$OUTPUT_DIR" ); fi

if [[ -n "${BLOCKFROST_PROJECT:-}" ]]; then CMD_ARGS+=( "--blockfrost-project" "$BLOCKFROST_PROJECT" ); fi

if [[ -n "${SINGLE_VEND_MAX:-}" ]]; then CMD_ARGS+=( "--single-vend-max" "$SINGLE_VEND_MAX" ); fi

if [[ "${VEND_RANDOMLY:-false}" == "true" ]]; then CMD_ARGS+=( "--vend-randomly" ); fi

if [[ -n "${DEV_FEE:-}" ]]; then CMD_ARGS+=( "--dev-fee" "$DEV_FEE" ); fi
if [[ -n "${DEV_ADDR:-}" ]]; then CMD_ARGS+=( "--dev-addr" "$DEV_ADDR" ); fi

if [[ -n "${BOGO_THRESHOLD:-}" && -n "${BOGO_ADDITIONAL:-}" ]]; then
  CMD_ARGS+=( "--bogo" "$BOGO_THRESHOLD" "$BOGO_ADDITIONAL" )
fi

# Network selection
if [[ "${MAINNET:-false}" == "true" ]]; then CMD_ARGS+=( "--mainnet" ); fi
if [[ "${PREVIEW:-false}" == "true" ]]; then CMD_ARGS+=( "--preview" ); fi

# Whitelist selection
case "${WHITELIST_TYPE:-}" in
  "no") CMD_ARGS+=( "--no-whitelist" ) ;;
  "single_use_asset") if [[ -n "${WHITELIST_DIR:-}" ]]; then CMD_ARGS+=( "--single-use-asset-whitelist" "$WHITELIST_DIR" ); fi ;;
  "unlimited_asset") if [[ -n "${WHITELIST_DIR:-}" ]]; then CMD_ARGS+=( "--unlimited-asset-whitelist" "$WHITELIST_DIR" ); fi ;;
  "wallet") if [[ -n "${WHITELIST_DIR:-}" ]]; then CMD_ARGS+=( "--wallet-whitelist" "$WHITELIST_DIR" ); fi ;;
esac

# Subcommand: validate or run (default run)
SUBCMD=${SUBCOMMAND:-run}

set -x
exec python3 /app/main.py "$SUBCMD" "${CMD_ARGS[@]}"


