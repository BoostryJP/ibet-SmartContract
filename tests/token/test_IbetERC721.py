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
    def test_normal_1(self, IbetERC721, users):
        issuer = users["issuer"]

        # deploy
        token = issuer.deploy(IbetERC721)

        # assertion
        assert token.name() == "IbetERC721"
        assert token.balanceOf(issuer.address) == 0


class TestSafeMint:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, IbetERC721, users):
        issuer = users["issuer"]

        # deploy
        token = issuer.deploy(IbetERC721)

        # mint
        token.safeMint(issuer.address, 123, {"from": issuer})

        # assertion
        assert token.name() == "IbetERC721"
        assert token.balanceOf(issuer.address) == 1
        assert token.ownerOf(123) == issuer.address

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    def test_error_1(self, IbetERC721, users):
        issuer = users["issuer"]
        other = users["user1"]

        # deploy
        token = issuer.deploy(IbetERC721)

        # mint
        with brownie.reverts(revert_msg="Ownable: caller is not the owner"):
            token.safeMint(issuer.address, 123, {"from": other})
