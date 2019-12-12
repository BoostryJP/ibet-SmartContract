#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル
populus compile

# test実施
pytest --disable-pytest-warnings -v