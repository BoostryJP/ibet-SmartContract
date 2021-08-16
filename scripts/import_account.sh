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

# Import account (private key)
function import_account() {
  source ~/.bash_profile
  cd /app/ibet-SmartContract

  if [ -e ~/.brownie/accounts/deploy_user.json ]; then
    brownie accounts delete deploy_user
  fi

  # AWS Secrets Manager を利用する場合
  # AWS Secrets Manager より keystore file 形式の秘密鍵を読み込み
  AWS_REGION_NAME=${AWS_REGION_NAME:-ap-northeast-1}
  SECRETS_KEYSTORE_TMP_PATH="./data/secrets_keystore.json"

  function del_tmp_file() {
    rm -f ${SECRETS_KEYSTORE_TMP_PATH}
  }

  if [ ! -z "${AWS_SECRETS_ID}" ]; then
    SECRETS=$(aws secretsmanager get-secret-value --region "${AWS_REGION_NAME}" --secret-id "${AWS_SECRETS_ID}")
    if [ $? -ne 0 ]; then
      exit 1
    fi
    SECRET_STRING=$(echo "${SECRETS}" | jq -r '.SecretString')
    if [ $? -ne 0 ]; then
      exit 1
    fi
    echo "${SECRET_STRING}" | jq '' > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      # JSON形式であればKeystoreFileとみなしてファイル保存
      ETH_KEYSTORE_PATH=${SECRETS_KEYSTORE_TMP_PATH}
      echo "${SECRET_STRING}" > ${ETH_KEYSTORE_PATH}
      trap del_tmp_file 0 1 2 3 15
    else
      ETH_PRIVATE_KEY="${SECRET_STRING}"
      ETH_KEYSTORE_PATH=
    fi
  fi

  # ローカルアカウントの作成
  # AWS_SECRETS_ID > ETH_KEYSTORE_PATH > ETH_PRIVATE_KEY で優先される
  # NOTE: brownie はLANG等でローカライズされないため固定の英語応答文字列で待ち合わせる
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
      catch wait result
      set status [ lindex \$result 3 ]
      exit \$status
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
      catch wait result
      set status [ lindex \$result 3 ]
      exit \$status
    " || exit 1
    REFER_ACCOUNT=PRIVATEKEY
  else
    REFER_ACCOUNT=GETH
  fi

}