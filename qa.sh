#!/bin/bash
source ~/.bash_profile

cd /app/tmr-sc

# コントラクトコードのコンパイル
populus compile

# test実施
py.test tests/ --disable-pytest-warnings
