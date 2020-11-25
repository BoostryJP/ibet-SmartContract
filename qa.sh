#!/bin/bash

# Copyright BOOSTRY Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed onan "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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
