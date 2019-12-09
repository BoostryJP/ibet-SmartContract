pragma solidity ^0.4.24;

import "./Ownable.sol";

contract PaymentGateway is Ownable {

    // 収納代行業者（Agent）のリスト
    address[30] public agents;

    // 振込用銀行口座
    struct PaymentAccount {
        address account_address; // アカウントアドレス
        address agent_address; // 収納代行業者（Agent）のアドレス
        string encrypted_info; // 銀行口座情報（暗号化済）
        uint8 approval_status; // 認可状況（NONE(0)/NG(1)/OK(2)/WARN(3)/BAN(4)）
    }

    // 最新の版番
    // agent_address => 版番
    mapping(address => uint16) public latest_terms_version;

    // 振込用銀行口座情報
    // account_address => agent_address => PaymentAccount
    mapping(address => mapping(address => PaymentAccount)) public payment_accounts;

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

    // ファンクション：（管理者）収納代行業者（Agent）の追加
    function addAgent(uint _agent_id, address _agent_address)
        public
        onlyOwner()
        returns (uint)
    {
        require(_agent_id >= 0 && _agent_id <= 29);
        agents[_agent_id] = _agent_address;
        return _agent_id;
    }

    function getAgents() public view returns (address[30] memory) {
        return agents;
    }

    // ファンクション：支払情報を登録する
    //  ２回目以降は上書き登録を行う
    function register(address _agent_address, string memory _encrypted_info)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[msg.sender][_agent_address];
        require(payment_account.approval_status != 4);

        // 口座情報の登録
        payment_account.account_address = msg.sender;
        payment_account.agent_address = _agent_address;
        payment_account.encrypted_info = _encrypted_info;
        payment_account.approval_status = 1;

        emit Register(msg.sender, _agent_address);
        return true;
    }

    // ファンクション：（収納代行業者）口座情報を承認する
    function approve(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0x0000000000000000000000000000000000000000);

        payment_account.approval_status = 2;

        emit Approve(_account_address, msg.sender);
        return true;
    }

    // ファンクション：（収納代行業者）口座情報を警告状態にする
    function warn(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0x0000000000000000000000000000000000000000);

        payment_account.approval_status = 3;

        emit Warn(_account_address, msg.sender);
        return true;
    }

    // ファンクション：（収納代行業者）口座情報を非承認にする
    function unapprove(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0x0000000000000000000000000000000000000000);

        payment_account.approval_status = 1;

        emit Unapprove(_account_address, msg.sender);
        return true;
    }

    // ファンクション：（収納代行業者）口座情報をアカウント停止（BAN）する。
    function ban(address _account_address) public returns (bool) {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != 0x0000000000000000000000000000000000000000);

        payment_account.approval_status = 4;

        emit Ban(_account_address, msg.sender);
        return true;
    }

    // ファンクション：アカウントの承認状況を返却する
    function accountApproved(address _account_address, address _agent_address)
        public
        view
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][_agent_address];
        // アカウントが登録済み、かつ承認済みである場合、trueを返す
        if (payment_account.account_address != 0x0000000000000000000000000000000000000000 &&
            payment_account.approval_status == 2)
        {
            return true;
        } else {
            return false;
        }
    }

}
