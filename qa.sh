#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# コントラクトコードのコンパイル（キャッシュを使わずフルビルド）
brownie compile --all

TEST_LOG=$(mktemp)

# test実施
brownie test --disable-warnings -v --network dev_network | tee "${TEST_LOG}"

# `brownie test`のリターンコードはテスト結果に関わらず常に正常となるので、
# コンソール出力内容からテスト結果を判定する
PYTEST_ERRORS_HEADER="=========== ERRORS ==========="
PYTEST_FAILURES_HEADER="=========== FAILURES ==========="
if grep -e "${PYTEST_ERRORS_HEADER}" -e "${PYTEST_FAILURES_HEADER}" "${TEST_LOG}" > /dev/null; then
  # pytest結果NG
  exit 1
fi

rm "${TEST_LOG}"
