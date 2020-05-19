#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル（キャッシュを使わずフルビルド）
brownie compile --all

# deploy実施
python scripts/contract_deploy.py