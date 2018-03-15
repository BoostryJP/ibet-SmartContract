pragma solidity ^0.4.19;

contract WhiteList {

    // 支払用口座
    struct PaymentAccount {
        address account_address; // アカウントアドレス
        address agent_address; // アカウントアドレス（決済業者）
        string encrypted_info; // 銀行口座情報（暗号化済）
        string approval_status; // 承認状態（OK/NG/WARN）
    }

    // 支払用口座情報
    // account_address => agent_address => PaymentAccount
    mapping(address => mapping(address => PaymentAccount)) public payment_accounts;

    // イベント：登録
    event Register(address indexed account_address, address indexed agent_address);

    // イベント：登録内容変更
    event ChangeInfo(address indexed account_address, address indexed agent_address);

    // イベント：承認
    event Approve(address indexed account_address, address indexed agent_address);

    // イベント：警告
    event Warn(address indexed account_address, address indexed agent_address);

    // イベント：非承認
    event Unapprove(address indexed account_address, address indexed agent_address);

    // コンストラクタ
    function WhiteList() public {
    }

    // 投資家：支払情報を登録する
    function register(address _agent_address, string _encrypted_info) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[msg.sender][_agent_address];
        require(payment_account.account_address == 0);

        payment_account.account_address = msg.sender;
        payment_account.agent_address = _agent_address;
        payment_account.encrypted_info = _encrypted_info;
        payment_account.approval_status = 'NG';

        Register(msg.sender, _agent_address);

        return true;
    }

    // 投資家：支払情報の更新
    function changeInfo(address _agent_address, string _encrypted_info) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[msg.sender][_agent_address];
        require(payment_account.account_address != 0);

        payment_account.encrypted_info = _encrypted_info;
        payment_account.approval_status = 'NG';

        ChangeInfo(msg.sender, _agent_address);

        return true;
    }

    // 決済業者：支払情報を承認する
    function approve(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 'OK';

        Approve(_account_address, msg.sender);

        return true;
    }

    // 決済業者：支払情報を警告状態にする
    function warn(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 'WARN';

        Warn(_account_address, msg.sender);

        return true;
    }

    // 決済業者：支払情報を非承認にする
    function unapprove(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 'NG';

        Unapprove(_account_address, msg.sender);

        return true;
    }

}
