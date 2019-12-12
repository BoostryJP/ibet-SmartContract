#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル
populus compile

# deploy実施
python scripts/contract_deploy.py