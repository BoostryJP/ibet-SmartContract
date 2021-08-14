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


deploy_args = [
    'test_share',  # name
    'test_symbol',  # symbol
    100000,  # total supply
    brownie.ZERO_ADDRESS,  # tradable exchange
    'test_contact_information',
    'test_privacy_policy'
]


# TEST_register
class TestRegister:

    #######################################
    # Normal
    #######################################
    
    # Normal_1
    def test_normal_1(self, users, ContractRegistry, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']
    
        # deploy
        contract_registry = admin.deploy(ContractRegistry)
    
        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register
        tx = contract_registry.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert contract_registry.getRegistry(token.address) == (
            'IbetStandardToken',
            issuer.address
        )

        assert tx.events["Registered"]["contractAddress"] == token.address
        assert tx.events["Registered"]["contractType"] == 'IbetStandardToken'
        assert tx.events["Registered"]["contractOwner"] == issuer.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Need to set the address of contract.
    def test_error_1(self, users, ContractRegistry):
        admin = users['admin']

        # deploy
        contract_registry = admin.deploy(ContractRegistry)

        # register to list
        with brownie.reverts(revert_msg="Need to set the address of contract."):
            contract_registry.register.transact(
                brownie.ZERO_ADDRESS,
                'IbetStandardToken',
                {'from': users["user1"]}
            )

    # Error_2
    # The msg.sender must be the owner of the contract.
    def test_error_2(self, users, ContractRegistry, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        contract_registry = admin.deploy(ContractRegistry)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        with brownie.reverts(revert_msg="The msg.sender must be the owner of the contract."):
            contract_registry.register.transact(
                token.address,
                'IbetStandardToken',
                {'from': users["user1"]}
            )


# TEST_getRegistry
class TestGetRegistry:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, ContractRegistry, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        contract_registry = admin.deploy(ContractRegistry)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        contract_registry.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert contract_registry.getRegistry(token.address) == (
            'IbetStandardToken',
            issuer.address
        )
