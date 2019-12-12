#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル
populus compile

# IbetSwapコントラクト：決済トークン設定（setSettlementToken）
python scripts/IbetSwap_setSettlementToken.py $1 $2