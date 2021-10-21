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

source ~/.bash_profile

cd /app/ibet-SmartContract/e2e_tests

# Load environment variables
if [ -z "${WEB3_HTTP_PROVIDER}" ]; then

  # Get main brownie project's network configure
  APP_ENV=${APP_ENV:-local}
  NETWORKS=$(NETWORK_ID="${APP_ENV}_network" python -c '
import os
from brownie import network
from brownie.network.main import CONFIG
network.connect(os.environ.get("NETWORK_ID"))
active_network = CONFIG.active_network
host = active_network["host"]
chain_id = active_network["chainid"]
gas_limit = active_network["settings"]["gas_limit"]
print(f"{host} {chain_id} {gas_limit}")
') || exit 1
  WEB3_HTTP_PROVIDER=$(echo ${NETWORKS} | awk '{print $1}')
  CHAIN_ID=$(echo ${NETWORKS} | awk '{print $2}')
  TX_GAS_LIMIT=$(echo ${NETWORKS} | awk '{print $3}')
  if [ "${TX_GAS_LIMIT}" == "auto" ]; then
    TX_GAS_LIMIT=
  fi
fi
export WEB3_HTTP_PROVIDER
export CHAIN_ID=${CHAIN_ID:-2017}
export TX_GAS_LIMIT=${TX_GAS_LIMIT:-6000000}
export DEPLOYED_CONTRACT_ADDRESS=${DEPLOYED_CONTRACT_ADDRESS:-0x0000000000000000000000000000000000000000}
WEB3_VERSION=${WEB3_VERSION:-5.15.0}
cat << EOS

==============================================================
Use settings:
  WEB3_HTTP_PROVIDER=${WEB3_HTTP_PROVIDER}
  CHAIN_ID=${CHAIN_ID}
  TX_GAS_LIMIT=${TX_GAS_LIMIT}
  DEPLOYED_CONTRACT_ADDRESS=${DEPLOYED_CONTRACT_ADDRESS}
  WEB3_VERSION=${WEB3_VERSION}
  ETH_ACCOUNT_PASSWORD=${ETH_ACCOUNT_PASSWORD}

EOS

# Compile test contract
brownie compile --all || exit 1
echo

# Create test account
export ACCOUNT_NAME=test_user
export ACCOUNT_PASSWORD=password
brownie accounts list | grep "${ACCOUNT_NAME}" > /dev/null
if [ $? -ne 0 ]; then
  expect -c "
    spawn brownie accounts generate ${ACCOUNT_NAME}
    expect {
      \"Enter the password to encrypt this account with:\" {
        send \"${ACCOUNT_PASSWORD}\n\"
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
  brownie accounts export "${ACCOUNT_NAME}" "./${ACCOUNT_NAME}.json" || exit 1
  echo
fi

# Install target web3 version
# NOTE:
#   Because web3 cannot be installed due to Brownie's dependency, and Brownie hooks pytest and behaves unexpectedly,
#   it uninstall brownie.
pip uninstall -y eth-brownie > /dev/null 2>&1
pip install web3==${WEB3_VERSION} > /dev/null 2>&1
trap 'pip install -r ../requirements.txt > /dev/null 2>&1' 0 1 2 3 15

# Run test
pytest -vv || exit 1

# Deploy contract this version
CONTRACT_ADDRESS=$(python scripts/deploy.py) || exit 1
cat << EOS

==============================================================
Deploy contract for other test:
  DEPLOYED_CONTRACT_ADDRESS=${CONTRACT_ADDRESS}

EOS

exit 0