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
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

source ~/.profile

cd /app/ibet-SmartContract

# 秘密鍵のインポート
. scripts/import_account.sh
import_account

# コントラクトコードのコンパイル
# NOTE: キャッシュを使わずフルビルドを行う
brownie compile --all

# コントラクトデプロイ
export REFER_ACCOUNT
if [ "${REFER_ACCOUNT}" != "GETH" ]; then
  # NOTE: Accounts.load内で用いられているgetpassで入力待ちとなるためexpectで自動応答する
  expect -c "
    set timeout 300
    spawn python scripts/deploy_shared_contract.py $*
    expect {
      \"Enter password for \\\"deploy_user\\\": \" {
        send \"${ETH_ACCOUNT_PASSWORD}\n\"
        exp_continue
      }
      timeout {
        exit 1
      }
    }
    catch wait result
    set status [ lindex \$result 3 ]
    exit \$status
  " || exit 1
else
  python scripts/deploy_shared_contract.py "$@"
fi