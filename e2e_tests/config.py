"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""
import os

# Used common
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Refer environment variables
ACCOUNT_NAME = os.environ.get('ACCOUNT_NAME') or "test_user"
ACCOUNT_PASSWORD = os.environ.get('ACCOUNT_PASSWORD') or "password"
WEB3_HTTP_PROVIDER = os.environ.get('WEB3_HTTP_PROVIDER') or 'http://localhost:8545'
CHAIN_ID = int(os.environ.get("CHAIN_ID")) if os.environ.get("CHAIN_ID") else 2017
TX_GAS_LIMIT = int(os.environ.get("TX_GAS_LIMIT")) if os.environ.get("TX_GAS_LIMIT") else 6000000
DEPLOYED_CONTRACT_ADDRESS = os.environ.get('DEPLOYED_CONTRACT_ADDRESS') or ZERO_ADDRESS
ETH_ACCOUNT_PASSWORD = os.environ.get('ETH_ACCOUNT_PASSWORD')
