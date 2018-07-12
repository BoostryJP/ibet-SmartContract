pragma solidity ^0.4.24;

contract WhiteList {

    // 利用規約同意
    struct Agreement {
        address account_address; // アカウントアドレス
        address agent_address; // アカウントアドレス（決済業者）
        bool status; // 同意状況（同意済:true）
    }

    // 利用規約
    // agent_address => 規約本文
    mapping(address => string) public terms;

    // 利用規約同意情報
    // account_address => agent_address => Agreement
    mapping(address => mapping(address => Agreement)) public agreements;

    // 支払用口座
    struct PaymentAccount {
        address account_address; // アカウントアドレス
        address agent_address; // アカウントアドレス（決済業者）
        string encrypted_info; // 銀行口座情報（暗号化済）
        uint8 approval_status; // 承認状態（NONE(0)/NG(1)/OK(2)/WARN(3)/BAN(4)）
    }

    // 支払用口座情報
    // account_address => agent_address => PaymentAccount
    mapping(address => mapping(address => PaymentAccount)) public payment_accounts;

    // イベント：規約同意
    event Agree(address indexed account_address, address indexed agent_address);

    // イベント：登録
    event Register(address indexed account_address, address indexed agent_address);

    // イベント：承認
    event Approve(address indexed account_address, address indexed agent_address);

    // イベント：警告
    event Warn(address indexed account_address, address indexed agent_address);

    // イベント：非承認
    event Unapprove(address indexed account_address, address indexed agent_address);

    // イベント：アカウント停止（BAN）
    event Ban(address indexed account_address, address indexed agent_address);

    // コンストラクタ
    constructor() public {
    }

    // ファンクション：（決済業者）利用規約登録
    function register_terms(string _text) public returns (bool) {
        terms[msg.sender] = _text;
        return true;
    }

    // ファンクション：利用規約同意
    function agree_terms(address _account_address, address _agent_address)
        private
        returns (bool)
    {
        Agreement storage agreement = agreements[_account_address][_agent_address];
        agreement.account_address = _account_address;
        agreement.agent_address = _agent_address;
        agreement.status = true;

        emit Agree(_account_address, _agent_address);

        return true;
    }

    // ファンクション：（投資家）支払情報を登録する
    //  ２回目以降は上書き登録を行う
    function register(address _agent_address, string _encrypted_info) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[msg.sender][_agent_address];
        require(payment_account.approval_status != 4);

        payment_account.account_address = msg.sender;
        payment_account.agent_address = _agent_address;
        payment_account.encrypted_info = _encrypted_info;
        payment_account.approval_status = 1;

        // 利用規約同意
        agree_terms(msg.sender, _agent_address);

        emit Register(msg.sender, _agent_address);

        return true;
    }

    // ファンクション：（決済業者）支払情報を承認する
    function approve(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 2;

        emit Approve(_account_address, msg.sender);

        return true;
    }

    // ファンクション：（決済業者）支払情報を警告状態にする
    function warn(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 3;

        emit Warn(_account_address, msg.sender);

        return true;
    }

    // ファンクション：（決済業者）支払情報を非承認にする
    function unapprove(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 1;

        emit Unapprove(_account_address, msg.sender);

        return true;
    }

    // ファンクション：（決済業者）支払情報をアカウント停止（BAN）する。
    function ban(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0);

        payment_account.approval_status = 4;

        emit Ban(_account_address, msg.sender);

        return true;
    }

    // ファンクション：登録状況を確認する
    function isRegistered(address _account_address, address _agent_address) public view returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][_agent_address];
        // アカウントが登録済み、かつ承認済みである場合、trueを返す
        if (payment_account.account_address != 0 && payment_account.approval_status == 2) {
            return true;
        } else {
            return false;
        }
    }

}
