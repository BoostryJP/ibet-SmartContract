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

# AWS Secrets Manager
if [ ! -z "${AWS_SECRETS_ID}" ]; then
  SECRETS=$(aws secretsmanager get-secret-value --secret-id  "${AWS_SECRETS_ID}" | jq -r '.SecretString')
  if [ $? -ne 0 ]; then
    exit 1
  fi
  echo "${SECRETS}" | jq '' > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    # JSON形式であればKeystoreFileとみなしてファイル保存
    ETH_KEYSTORE_PATH="/tmp/keystore.json"
    echo "${SECRETS}" > ${ETH_KEYSTORE_PATH}
  else
    ETH_PRIVATE_KEY="${SECRETS}"
  fi
fi

# ローカルアカウントの作成( AWS_SECRETS_ID > ETH_KEYSTORE_PATH > ETH_PRIVATE_KEY で優先される)
# NOTE: brownieはLANG等でローカライズされないため固定の英語応答文字列で待ち合わせる
ETH_ACCOUNT_PASSWORD=${ETH_ACCOUNT_PASSWORD:-password}
if [ ! -z "${ETH_KEYSTORE_PATH}" ]; then
  expect -c "
    spawn brownie accounts import deploy_user ${ETH_KEYSTORE_PATH}
    expect {
      \"Enter the password to unlock this account:\" {
        send \"${ETH_ACCOUNT_PASSWORD}\n\"
        exp_continue
      }
      \"SUCCESS: Keystore\" {
        exit 0
      }
      timeout {
        exit 1
      }
    }
  " || exit 1
  REFER_ACCOUNT=KEYSTORE
elif [ ! -z "${ETH_PRIVATE_KEY}" ]; then
    expect -c "
    spawn brownie accounts new deploy_user
    expect {
      \"Enter the private key you wish to add:\" {
        send \"${ETH_PRIVATE_KEY}\n\"
        exp_continue
      }
      \"Enter the password to encrypt this account with:\" {
        send \"${ETH_ACCOUNT_PASSWORD}\n\"
        exp_continue
      }
      \"SUCCESS: A new account\" {
        exit 0
      }
      timeout {
        exit 1
      }
    }
  " || exit 1
  REFER_ACCOUNT=PRIVATEKEY
else
  REFER_ACCOUNT=GETH
fi

# deploy実施
export REFER_ACCOUNT
if [ "${REFER_ACCOUNT}" != "GETH" ]; then
  # NOTE: Accounts.load内で用いられているgetpassで入力待ちとなるためexpectで自動応答
  expect -c "
    set timeout 300
    spawn python scripts/contract_deploy.py
    expect {
      \"Enter the password to unlock this account:\" {
        send \"${ETH_ACCOUNT_PASSWORD}\n\"
        exp_continue
      }
      timeout {
        exit 1
      }
    }
  "
else
  python scripts/contract_deploy.py
fi
