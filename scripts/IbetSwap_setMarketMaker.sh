#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル
populus compile

# IbetSwapコントラクト：マーケットメイカー設定（setMarketMaker）
python scripts/IbetSwap_setMarketMaker.py $1 $2 $3