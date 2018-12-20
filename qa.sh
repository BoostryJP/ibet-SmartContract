#!/bin/bash
source ~/.bash_profile

cd /app/tmr-sc

# コントラクトコードのコンパイル
populus compile

# test実施
py.test tests/ --disable-pytest-warnings -v --cov=contracts/ --cov-report=xml --cov-branch

# カバレッジファイルの移動
mv coverage.xml cov/
