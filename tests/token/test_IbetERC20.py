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

import brownie


class TestDeploy:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, IbetERC20, users):
        issuer = users["issuer"]

        # deploy
        token = issuer.deploy(IbetERC20)

        # assertion
        assert token.name() == "IbetERC20"
        assert token.symbol() == ""
        assert token.decimals() == 18
        assert token.totalSupply() == 0
        assert token.balanceOf(issuer.address) == 0


class TestMint:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, IbetERC20, users):
        issuer = users["issuer"]

        # deploy
        token = issuer.deploy(IbetERC20)

        # mint
        token.mint(issuer.address, 10, {"from": issuer})

        # assertion
        assert token.name() == "IbetERC20"
        assert token.symbol() == ""
        assert token.decimals() == 18
        assert token.totalSupply() == 10
        assert token.balanceOf(issuer.address) == 10

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    def test_error_1(self, IbetERC20, users):
        issuer = users["issuer"]
        other = users["user1"]

        # deploy
        token = issuer.deploy(IbetERC20)

        # mint
        with brownie.reverts(revert_msg="Ownable: caller is not the owner"):
            token.mint(issuer.address, 10, {"from": other})
