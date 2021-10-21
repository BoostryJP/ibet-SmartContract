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
import logging
import pytest

from tests.util import ContractUtils

logging.getLogger("web3.providers.HTTPProvider")
logging.basicConfig(level="DEBUG")


@pytest.fixture(scope="function")
def contract():
    args = [
        True,
        "0x0123456789abcDEF0123456789abCDef01234567",
        "test text",
        1,
        2,
        b'abc'
    ]
    contract_address, _, _ = ContractUtils.deploy_contract(args)
    return ContractUtils.get_contract(contract_address)
