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

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'
terms_text = 'terms_sample\nend'
terms_text_after = 'terms_sample\nafter\nend'


# TEST_deploy
class TestDeploy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == brownie.ZERO_ADDRESS
        assert payment_account[1] == brownie.ZERO_ADDRESS
        assert payment_account[2] == ''
        assert payment_account[3] == 0

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False


# TEST_register
class TestRegister:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        tx = pg_contract.register.transact(
            agent,
            encrypted_message,
            {'from': trader}
        )

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 1

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False

        assert tx.events['Register']['account_address'] == trader.address
        assert tx.events['Register']['agent_address'] == agent.address

    # Normal_2
    # Multiple registrations
    def test_normal_2(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register (1)
        pg_contract.register.transact(
            agent,
            encrypted_message,
            {'from': trader}
        )

        # register (2)
        pg_contract.register.transact(
            agent,
            encrypted_message_after,
            {'from': trader}
        )

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message_after
        assert payment_account[3] == 1

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False

    #######################################
    # Error
    #######################################

    # Error_1
    # If approval_status = 4 (BAN), registration is not possible.
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register (1)
        pg_contract.register.transact(
            agent,
            encrypted_message,
            {'from': trader}
        )

        # ban
        pg_contract.ban.transact(trader, {'from': agent})

        # register (2)
        with brownie.reverts(revert_msg="300001"):
            pg_contract.register.transact(
                agent,
                encrypted_message_after,
                {'from': trader}
            )

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 4

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False


# TEST_modify
class TestModify:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(
            agent,
            encrypted_message,
            {'from': trader}
        )

        # modify
        tx = pg_contract.modify.transact(
            trader,
            encrypted_message_after,
            {'from': agent}
        )

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message_after
        assert payment_account[3] == 1

        assert tx.events['Modify']['account_address'] == trader.address
        assert tx.events['Modify']['agent_address'] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # modify
        with brownie.reverts(revert_msg="300501"):
            pg_contract.modify.transact(
                trader,
                encrypted_message_after,
                {'from': agent}
            )

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == brownie.ZERO_ADDRESS
        assert payment_account[1] == brownie.ZERO_ADDRESS
        assert payment_account[2] == ''
        assert payment_account[3] == 0

    # Error_2
    # Unauthorized
    def test_error_2(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(
            agent,
            encrypted_message,
            {'from': trader}
        )

        # modify
        with brownie.reverts(revert_msg="300501"):
            pg_contract.modify.transact(
                trader,
                encrypted_message_after,
                {'from': trader}
            )

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 1


# TEST_approve
class TestApprove:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(agent, encrypted_message, {'from': trader})

        # approve
        tx = pg_contract.approve.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 2

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is True

        assert tx.events['Approve']['account_address'] == trader.address
        assert tx.events['Approve']['agent_address'] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # approve
        with brownie.reverts(revert_msg="300101"):
            pg_contract.approve.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == brownie.ZERO_ADDRESS


# TEST_warn
class TestWarn:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(agent, encrypted_message, {'from': trader})

        # warn
        tx = pg_contract.warn.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 3

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False

        assert tx.events['Warn']['account_address'] == trader.address
        assert tx.events['Warn']['agent_address'] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # warn
        with brownie.reverts(revert_msg="300201"):
            pg_contract.warn.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == brownie.ZERO_ADDRESS


# TEST_disapprove
class TestDisapprove:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(agent, encrypted_message, {'from': trader})

        # disapprove
        tx = pg_contract.disapprove.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 1

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False

        assert tx.events['Disapprove']['account_address'] == trader.address
        assert tx.events['Disapprove']['agent_address'] == agent.address

    # Normal_2
    # register -> approve -> disapprove
    def test_normal_2(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(agent, encrypted_message, {'from': trader})

        # approve
        pg_contract.approve.transact(trader, {'from': agent})

        # disapprove
        pg_contract.disapprove.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 1

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # disapprove
        with brownie.reverts(revert_msg="300301"):
            pg_contract.disapprove.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == brownie.ZERO_ADDRESS


# TEST_ban
class TestBan:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # register
        pg_contract.register.transact(agent, encrypted_message, {'from': trader})

        # ban
        tx = pg_contract.ban.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == trader
        assert payment_account[1] == agent
        assert payment_account[2] == encrypted_message
        assert payment_account[3] == 4

        account_approved = pg_contract.accountApproved(trader, agent)
        assert account_approved is False

        assert tx.events['Ban']['account_address'] == trader.address
        assert tx.events['Ban']['agent_address'] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        trader = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # ban
        with brownie.reverts(revert_msg="300401"):
            pg_contract.ban.transact(trader, {'from': agent})

        # assertion
        payment_account = pg_contract.payment_accounts(trader, agent)
        assert payment_account[0] == brownie.ZERO_ADDRESS


# TEST_addAgent
class TestAddAgent:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Default value
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # assertion
        agent_available = pg_contract.getAgent(brownie.ZERO_ADDRESS)
        assert agent_available == False

    # Normal_2
    # Add new agent
    def test_normal_2(self, PaymentGateway, users):
        admin = users['admin']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # add agent
        tx = pg_contract.addAgent.transact(agent, {'from': admin})

        # assertion
        agent_available = pg_contract.getAgent(agent)
        assert agent_available == True

        assert tx.events['AddAgent']['agent_address'] == agent.address

    # Normal_3
    # Add multiple agents
    def test_normal_3(self, PaymentGateway, users):
        admin = users['admin']
        agent_1 = users['user1']
        agent_2 = users['user2']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # add agent 1
        pg_contract.addAgent.transact(agent_1, {'from': admin})

        # add agent 2
        pg_contract.addAgent.transact(agent_2, {'from': admin})

        # assertion
        agent_1_available = pg_contract.getAgent(agent_1)
        assert agent_1_available == True

        agent_2_available = pg_contract.getAgent(agent_2)
        assert agent_2_available == True

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        attacker = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # add agent
        with brownie.reverts(revert_msg="500001"):
            pg_contract.addAgent.transact(agent, {'from': attacker})

        # assertion
        agent_available = pg_contract.getAgent(agent)
        assert agent_available == False


# TEST_removeAgent
class TestRemoveAgent:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # No data
    def test_normal_1(self, PaymentGateway, users):
        admin = users['admin']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # remove agent
        tx = pg_contract.removeAgent.transact(agent, {'from': admin})

        # assertion
        agent_available = pg_contract.getAgent(agent)
        assert agent_available == False

        assert tx.events['RemoveAgent']['agent_address'] == agent.address


    # Normal_2
    def test_normal_2(self, PaymentGateway, users):
        admin = users['admin']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # add agent
        pg_contract.addAgent.transact(agent, {'from': admin})

        # remove agent
        tx = pg_contract.removeAgent.transact(agent, {'from': admin})

        # assertion
        agent_available = pg_contract.getAgent(agent)
        assert agent_available == False

        assert tx.events['RemoveAgent']['agent_address'] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, PaymentGateway, users):
        admin = users['admin']
        attacker = users['trader']
        agent = users['agent']

        # deploy
        pg_contract = admin.deploy(PaymentGateway)

        # add agent
        pg_contract.addAgent.transact(agent, {'from': admin})

        # remove agent
        with brownie.reverts(revert_msg="500001"):
            pg_contract.removeAgent.transact(agent, {'from': attacker})

        # assertion
        agent_available = pg_contract.getAgent(agent)
        assert agent_available == True
