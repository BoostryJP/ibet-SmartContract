pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";
import "./IbetStandardTokenInterface.sol";
import "./PersonalInfo.sol";


contract IbetShare is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint256;

    // 関連アドレス情報
    address public personalInfoAddress; // 個人情報記帳コントラクト
    mapping(address => bool) public authorizedAddress; // 認可済みコントラクト

    // 属性情報
    uint256 public issuePrice; // 発行価格
    // 配当情報
    struct DividendInformation {
        uint256 dividends; // 1口あたりの配当金/分配金
        string dividendRecordDate; // 権利確定日
        string dividendPaymentDate; // 配当支払日
    }
    DividendInformation public dividendInformation;
    string public cancellationDate; // 消却日
    mapping(uint8 => string) public referenceUrls; // 関連URL
    string public memo; // 補足情報

    // 状態を示す属性
    bool public transferable; // 譲渡可能
    bool public offeringStatus; // 募集ステータス（True：募集中、False：停止中）

    // 残高数量 account_address => balance
    mapping(address => uint256) public balances;

    // ロック資産数量 address => account_address => balance
    mapping(address => mapping(address => uint256)) public locked;

    // 募集申込情報
    struct Application {
        uint256 requestedAmount; // 申込数量
        string data; // その他データ
    }
    // 募集申込 account_address => data
    mapping(address => Application) public applications;

    // イベント：認可
    event Authorize(address indexed to, bool auth);

    // イベント：資産ロック
    event Lock(address indexed _target_address, uint256 value);

    // イベント：資産アンロック
    event Unlock(address indexed from, address indexed to, uint256 value);

    // イベント：配当情報の変更
    event ChangeDividendInformation(
        uint256 dividends,
        string dividendRecordDate,
        string dividendPaymentDate
    );

    // イベント：振替
    event Transfer(address indexed from, address indexed to, uint256 value);

    // イベント：ステータス変更
    event ChangeStatus(bool indexed status);

    // イベント：募集ステータス変更
    event ChangeOfferingStatus(bool indexed status);

    // イベント：募集申込
    event ApplyFor(address indexed accountAddress, uint256 amount);

    // イベント：増資
    event Issue(address indexed from, address indexed target_address, address indexed locked_address, uint256 amount);

    // イベント：減資
    event Redeem(address indexed from, address indexed target_address, address indexed locked_address, uint256 amount);

    // コンストラクタ
    constructor(
        string memory _name,
        string memory _symbol,
        address _tradableExchange,
        address _personalInfoAddress,
        uint256 _issuePrice,
        uint256 _totalSupply,
        uint256 _dividends,
        string memory _dividendRecordDate,
        string memory _dividendPaymentDate,
        string memory _cancellationDate,
        string _contactInformation,
        string _privacyPolicy,
        string memory _memo,
        bool _transferable
    ) public {
        name = _name;
        symbol = _symbol;
        owner = msg.sender;
        tradableExchange = _tradableExchange;
        personalInfoAddress = _personalInfoAddress;
        issuePrice = _issuePrice;
        totalSupply = _totalSupply;
        dividendInformation.dividends = _dividends;
        dividendInformation.dividendRecordDate = _dividendRecordDate;
        dividendInformation.dividendPaymentDate = _dividendPaymentDate;
        cancellationDate = _cancellationDate;
        contactInformation = _contactInformation;
        privacyPolicy = _privacyPolicy;
        memo = _memo;
        status = true;
        transferable = _transferable;
        balances[owner] = totalSupply;
    }

    // ファンクション：取引可能Exchangeの更新
    // オーナーのみ実行可能
    function setTradableExchange(address _exchange) public onlyOwner() {
        tradableExchange = _exchange;
    }

    // ファンクション：個人情報記帳コントラクトの更新
    // オーナーのみ実行可能
    function setPersonalInfoAddress(address _address) public onlyOwner() {
        personalInfoAddress = _address;
    }

    // ファンクション：配当情報の更新
    // オーナーのみ実行可能
    function setDividendInformation(
        uint256 _dividends,
        string _dividendRecordDate,
        string _dividendPaymentDate
    ) public onlyOwner() {
        dividendInformation.dividends = _dividends;
        dividendInformation.dividendRecordDate = _dividendRecordDate;
        dividendInformation.dividendPaymentDate = _dividendPaymentDate;
        emit ChangeDividendInformation(
            dividendInformation.dividends,
            dividendInformation.dividendRecordDate,
            dividendInformation.dividendPaymentDate
        );
    }

    // ファンクション：消却日の更新
    // オーナーのみ実行可能
    function setCancellationDate(string _cancellationDate) public onlyOwner() {
        cancellationDate = _cancellationDate;
    }

    // ファンクション：商品の関連URLを設定する
    // オーナーのみ実行可能
    function setReferenceUrls(uint8 _class, string memory _referenceUrl)
        public
        onlyOwner()
    {
        referenceUrls[_class] = _referenceUrl;
    }

    // ファンクション：問い合わせ先情報更新
    function setContactInformation(string _contactInformation)
        public
        onlyOwner()
    {
        contactInformation = _contactInformation;
    }

    // ファンクション：プライバシーポリシー更新
    function setPrivacyPolicy(string _privacyPolicy) public onlyOwner() {
        privacyPolicy = _privacyPolicy;
    }

    // ファンクション：メモ欄を更新する
    function setMemo(string memory _memo) public onlyOwner() {
        memo = _memo;
    }

    // ファンクション：ステータスの有効・無効を更新する
    // オーナーのみ実行可能
    function setStatus(bool _status) public onlyOwner() {
        status = _status;
        emit ChangeStatus(status);
    }

    // ファンクション：譲渡可能フラグを更新
    // オーナーのみ実行可能
    function setTransferable(bool _transferable) public onlyOwner() {
        transferable = _transferable;
    }

    // ファンクション：新規募集ステータス更新
    // オーナーのみ実行可能
    function setOfferingStatus(bool _status) public onlyOwner() {
        offeringStatus = _status;
        emit ChangeOfferingStatus(_status);
    }

    // ファンクション：残高確認
    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }

    // ファンクション：アドレス認可
    // オーナーのみ実行可能
    function authorize(address _address, bool _auth) public onlyOwner() {
        authorizedAddress[_address] = _auth;
        emit Authorize(_address, _auth);
    }

    // ファンクション：ロック済み資産確認
    function lockedOf(address _authorized_address, address _account_address)
        public
        view
        returns (uint256)
    {
        return locked[_authorized_address][_account_address];
    }

    // ファンクション：資産ロック
    function lock(address _target_address, uint256 _value) public {
        // ロック対象が認可済みであるか、発行者であることをチェック
        require(authorizedAddress[_target_address] == true || _target_address == owner);
        // ロック数量が保有を上回っている場合、エラー
        if (balanceOf(msg.sender) < _value) revert();

        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        locked[_target_address][msg.sender] = lockedOf(
            _target_address,
            msg.sender
        ).add(_value);
        emit Lock(_target_address, _value);
    }

    // ファンクション：資産アンロック
    // 認可済みアドレスあるいは発行体のみ実行可能
    function unlock(address _account_address, address _receive_address, uint256 _value) public {
        require(authorizedAddress[msg.sender] == true || msg.sender == owner);
        if (lockedOf(msg.sender, _account_address) < _value) revert();
        
        locked[msg.sender][_account_address] = lockedOf(
            msg.sender,
            _account_address
        ).sub(_value);
        balances[_receive_address] = balanceOf(_receive_address).add(_value);
        emit Unlock(_account_address, _receive_address, _value);
    }

    // ファンクション：アドレスフォーマットがコントラクトのものかを判断する
    function isContract(address _addr) private view returns (bool is_contract) {
        uint256 length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    // ファンクション：アドレスへの振替
    function transferToAddress(
        address _to,
        uint256 _value,
        bytes memory /*_data*/
    ) private returns (bool success) {
        // 個人情報登録有無のチェック。
        // 取引コントラクトからのtransferと、発行体へのtransferの場合はチェックを行わない。
        if (msg.sender != tradableExchange && _to != owner) {
            require(
                PersonalInfo(personalInfoAddress).isRegistered(_to, owner) ==
                    true
            );
        }
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    // ファンクション：コントラクトへの振替
    function transferToContract(address _to, uint256 _value, bytes memory _data)
        private
        returns (bool success)
    {
        require(_to == tradableExchange);
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    // ファンクション：トークンの送信
    function transfer(address _to, uint256 _value)
        public
        returns (bool success)
    {
        // <CHK>
        //  数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        if (msg.sender != tradableExchange) {
            // 譲渡可能ではない場合、エラーを返す
            require(transferable == true);
        }

        bytes memory empty;
        if (isContract(_to)) {
            return transferToContract(_to, _value, empty);
        } else {
            return transferToAddress(_to, _value, empty);
        }
    }

    // ファンクション：移転
    // オーナーのみ実行可能
    function transferFrom(address _from, address _to, uint256 _value)
        public
        onlyOwner()
        returns (bool success)
    {
        // <CHK>
        //  数量が送信元アドレス（from）の残高を超えている場合、エラーを返す
        if (balanceOf(_from) < _value) revert();

        bytes memory empty;

        if (isContract(_to)) {
            // 送信先アドレスがコントラクトアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
            ContractReceiver receiver = ContractReceiver(_to);
            receiver.tokenFallback(msg.sender, _value, empty);
        } else {
            // 送信先アドレスがアカウントアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
        }

        // イベント登録
        emit Transfer(_from, _to, _value);

        return true;
    }

    // ファンクション：募集申込
    function applyForOffering(uint256 _amount, string memory _data) public {
        // 申込ステータスが停止中の場合、エラーを返す
        require(offeringStatus == true);

        // 個人情報未登録の場合、エラーを返す
        require(
            PersonalInfo(personalInfoAddress).isRegistered(msg.sender, owner) ==
                true
        );

        applications[msg.sender].requestedAmount = _amount;
        applications[msg.sender].data = _data;
        emit ApplyFor(msg.sender, _amount);
    }

    // ファンクション：追加発行
    // オーナーのみ実行可能
    function issueFrom(address _target_address, address _locked_address, uint256 _amount)
        public
        onlyOwner()
    {
        bytes memory empty;

        if (_locked_address != 0) {
            // secondary_addressが0ではない場合はlock数量の増減
            locked[_target_address][_locked_address] = lockedOf(_target_address, _locked_address).add(_amount);
            totalSupply = totalSupply.add(_amount);
        } else {
            // 送信先アドレスがアカウントアドレスの場合
            balances[_target_address] = balanceOf(_target_address).add(_amount);
            totalSupply = totalSupply.add(_amount);
        }
        emit Issue(msg.sender, _target_address, _locked_address, _amount);
    }

    // ファンクション：減資
    // オーナーのみ実行可能
    function redeemFrom(address _target_address, address _locked_address, uint256 _amount)
        public
        onlyOwner()
    {
        bytes memory empty;

        if (_locked_address != 0) {
            // 送信先アドレスが認可済みコントラクトの場合
            // 減資数量が対象アドレスのロック数量を上回っている場合はエラーを返す
            if (lockedOf(_target_address, _locked_address) < _amount) revert();

            locked[_target_address][_locked_address] = lockedOf(_target_address, _locked_address).sub(_amount);
            totalSupply = totalSupply.sub(_amount);
        } else {
            // 送信先アドレスがアカウントアドレスの場合
            // 減資数量が対象アドレスの保有を上回っている場合はエラーを返す
            if (balances[_target_address] < _amount) revert();

            balances[_target_address] = balanceOf(_target_address).sub(_amount);
            totalSupply = totalSupply.sub(_amount);
        }
        emit Redeem(msg.sender, _target_address, _locked_address, _amount);
    }
}
