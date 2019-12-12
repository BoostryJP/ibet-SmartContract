#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル
populus compile

# 収納代行業者（Agent）アドレス登録
python scripts/PaymentGateway_addAgent.py $1 $2 $3