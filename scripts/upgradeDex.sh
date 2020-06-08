#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル（キャッシュを使わずフルビルド）
brownie compile --all

# DEXアップグレード実施
python scripts/dex_upgrade.py "$@"
