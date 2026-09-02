#!/bin/bash
set -eu

SMARTCONT_DIR=${TON_SMARTCONT_DIR:-/usr/share/ton/smartcont}
STATE_IDENTITY_PATH=${TON_STATE_IDENTITY_PATH:-/var/ton-work/db/state/IDENTITY}
REGENERATE_WALLETS=${REGENERATE_WALLETS:-true}

write_random_wallet_seed() {
  wallet_name=$1
  dd if=/dev/urandom of="$SMARTCONT_DIR/$wallet_name.pk" bs=32 count=1 status=none
}

regenerate_wallets() {
  for wallet_name in \
    main-wallet \
    config-master \
    validator \
    validator-1 \
    validator-2 \
    validator-3 \
    validator-4 \
    validator-5 \
    faucet \
    faucet-highload \
    faucet-basechain \
    faucet-highload-basechain \
    data-highload
  do
    rm -f "$SMARTCONT_DIR/$wallet_name.pk" "$SMARTCONT_DIR/$wallet_name.addr"
    write_random_wallet_seed "$wallet_name"
  done
}

if [ "${GENESIS:-false}" = "true" ] && [ "$REGENERATE_WALLETS" != "false" ] && [ ! -f "$STATE_IDENTITY_PATH" ]; then
  regenerate_wallets
fi

if [ "${GENESIS:-false}" = "true" ]; then
  export HIDE_PRIVATE_KEYS=false
fi

exec /scripts/start-node.sh "$@"