pragma solidity ^0.4.19;

contract WhiteList {

    // 支払用口座
    struct PaymentAccount {
        address account_address; // アカウントアドレス
        address agent_address; // アカウントアドレス（決済業者）
        string encrypted_info; // 銀行口座情報（暗号化済）
        bool confirmed; // 決済業者承認済みフラグ
    }

    // 支払用口座情報
    // account_address => agent_address => PaymentAccount
    mapping(address => mapping(address => PaymentAccount)) public payment_accounts;

    // イベント：登録
    event Register(address indexed account_address, address indexed agent_address);

    // イベント：承認
    event Confirm(address indexed account_address, address indexed agent_address);

    // コンストラクタ
    function WhiteList() public {
    }

    function register(address _agent_address, string _encrypted_info) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[msg.sender][_agent_address];
        require(payment_account.account_address == 0);

        payment_account.account_address = msg.sender;
        payment_account.agent_address = _agent_address;
        payment_account.encrypted_info = _encrypted_info;
        payment_account.confirmed = false;

        Register(msg.sender, _agent_address);

        return true;
    }

    function confirm(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.confirmed = true;

        Confirm(_account_address, msg.sender);

        return true;
    }

}
