#!/bin/bash
source ~/.bash_profile

cd /app/tmr-sc

# コントラクトコードのコンパイル
populus compile

# deploy実施
python deploy/contract_deploy.py