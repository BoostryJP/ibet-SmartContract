agent_address = '0xd950a0ba53af3f4f295500eee692598e31166ad9'

def test_register(web3,chain):
    personal_info_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')

    txn_hash = personal_info_contract.transact().register(agent_address,'encrypted_info')
    chain.wait.for_receipt(txn_hash)

    personal_info = personal_info_contract.call().personal_info(web3.eth.accounts[0], agent_address)
    assert personal_info[2] == 'encrypted_info'
