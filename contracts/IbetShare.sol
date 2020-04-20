pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";
import "./IbetStandardTokenInterface.sol";
import "./PersonalInfo.sol";

// @title ibet Share Token Contract
contract IbetShare is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint256;

    address public personalInfoAddress; // 個人情報記帳コントラクト
    mapping(address => bool) public authorizedAddress; // 認可済みコントラクト

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
    bool public transferable; // 譲渡可否
    bool public offeringStatus; // 募集ステータス（True：募集中、False：停止中）

    // 残高数量 account_address => balance
    mapping(address => uint256) public balances;

    // ロック資産数量 address => account_address => balance
    mapping(address => mapping(address => uint256)) public locked;

    // 募集申込情報
    struct Application {
        uint256 requestedAmount; // 申込数量
        string data; // 任意のデータ
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

    // [CONSTRUCTOR]
    // @param _name 名称
    // @param _symbol 略称
    // @param _tradableExchange 取引コントラクト
    // @param _personalInfoAddress 個人情報記帳コントラクト
    // @param _issuePrice 発行価格
    // @param _totalSupply 総発行数量
    // @param _dividends 1口あたりの配当金・分配金
    // @param _dividendRecordDate 権利確定日
    // @param _dividendPaymentDate 配当支払日
    // @param _cancellationDate 消却日
    // @param _contactInformation 問い合わせ先
    // @param _privacyPolicy プライバシーポリシー
    // @param _memo 補足情報
    // @param _transferable 譲渡可否
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

    // @dev 取引コントラクトの更新
    // @dev オーナーのみ実行可能
    // @param _exchange 取引コントラクトアドレス
    function setTradableExchange(address _exchange)
        public
        onlyOwner()
    {
        tradableExchange = _exchange;
    }

    // @dev 個人情報記帳コントラクトの更新
    // @dev オーナーのみ実行可能
    // @param _address 個人情報記帳コントラクトアドレス
    function setPersonalInfoAddress(address _address)
        public
        onlyOwner()
    {
        personalInfoAddress = _address;
    }

    // @dev 配当情報の更新
    // @dev オーナーのみ実行可能
    // @param _dividends 1口あたりの配当金・分配金
    // @param _dividendRecordDate 権利確定日
    // @param _dividendPaymentDate 配当支払日
    function setDividendInformation(uint256 _dividends, string _dividendRecordDate, string _dividendPaymentDate)
        public
        onlyOwner()
    {
        dividendInformation.dividends = _dividends;
        dividendInformation.dividendRecordDate = _dividendRecordDate;
        dividendInformation.dividendPaymentDate = _dividendPaymentDate;
        emit ChangeDividendInformation(
            dividendInformation.dividends,
            dividendInformation.dividendRecordDate,
            dividendInformation.dividendPaymentDate
        );
    }

    // @dev 消却日の更新
    // @dev オーナーのみ実行可能
    // @param _cancellationDate 消却日
    function setCancellationDate(string _cancellationDate) public onlyOwner() {
        cancellationDate = _cancellationDate;
    }

    // @dev トークンの関連URLを設定する
    // @dev オーナーのみ実行可能
    // @param _class 関連URL番号
    // @param _referenceUrl 関連URL
    function setReferenceUrls(uint8 _class, string memory _referenceUrl)
        public
        onlyOwner()
    {
        referenceUrls[_class] = _referenceUrl;
    }

    // @dev 問い合わせ先情報更新
    // @dev オーナーのみ実行可能
    // @param _contactInformation 問い合わせ先情報
    function setContactInformation(string _contactInformation)
        public
        onlyOwner()
    {
        contactInformation = _contactInformation;
    }

    // @dev プライバシーポリシー更新
    // @dev オーナーのみ実行可能
    // @param _privacyPolicy プライバシーポリシー
    function setPrivacyPolicy(string _privacyPolicy)
        public
        onlyOwner()
    {
        privacyPolicy = _privacyPolicy;
    }

    // @dev 補足情報の更新
    // @dev オーナーのみ実行可能
    // @param _memo 補足情報
    function setMemo(string memory _memo)
        public
        onlyOwner()
    {
        memo = _memo;
    }

    // @dev 取扱ステータスの有効・無効を更新する
    // @dev オーナーのみ実行可能
    // @param _status 取扱ステータス
    function setStatus(bool _status)
        public
        onlyOwner()
    {
        status = _status;
        emit ChangeStatus(status);
    }

    // @dev 譲渡可能フラグを更新
    // @dev オーナーのみ実行可能
    // @param _transferable 譲渡可否
    function setTransferable(bool _transferable)
        public
        onlyOwner()
    {
        transferable = _transferable;
    }

    // @dev 募集ステータス更新
    // @dev オーナーのみ実行可能
    // @param _status 募集ステータス
    function setOfferingStatus(bool _status)
        public
        onlyOwner()
    {
        offeringStatus = _status;
        emit ChangeOfferingStatus(_status);
    }

    // @dev 残高確認
    // @param _address 保有者アドレス
    // @return 残高数量
    function balanceOf(address _address)
        public
        view
        returns (uint256)
    {
        return balances[_address];
    }

    // @dev 資産ロック先アドレスの認可
    // @dev オーナーのみ実行可能
    // @param _address 認可対象のアドレス
    // @param _auth 認可状態（true:認可、false:未認可）
    function authorize(address _address, bool _auth)
        public
        onlyOwner()
    {
        authorizedAddress[_address] = _auth;
        emit Authorize(_address, _auth);
    }

    // @dev ロック済み資産参照
    // @param _authorized_address 資産ロック先アドレス（認可済）
    // @param _account_address 資産ロック対象アカウント
    // @return ロック済み数量
    function lockedOf(address _authorized_address, address _account_address)
        public
        view
        returns (uint256)
    {
        return locked[_authorized_address][_account_address];
    }

    // @dev 資産ロック
    // @param _target_address 資産をロックする先のアドレス
    // @param _value ロックする数量
    function lock(address _target_address, uint256 _value)
        public
    {
        // ロック対象が認可済みアドレス、まはは発行者アドレスであることをチェック
        require(
            authorizedAddress[_target_address] == true ||
            _target_address == owner
        );

        // ロック数量が保有数量を上回っている場合、エラーを変えす
        if (balanceOf(msg.sender) < _value) revert();

        // データ更新
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        locked[_target_address][msg.sender] = lockedOf(_target_address, msg.sender).add(_value);

        emit Lock(_target_address, _value);
    }

    // @dev 資産アンロック
    // @dev 認可済みアドレスあるいは発行体のみ実行可能
    // @param _account_address アンロック対象のアドレス
    // @param _receive_address 受取アドレス
    function unlock(address _account_address, address _receive_address, uint256 _value)
        public
    {
        // msg.senderが認可済みアドレス、または発行者アドレスであることをチェック
        require(
            authorizedAddress[msg.sender] == true ||
            msg.sender == owner
        );

        // アンロック数量がロック数量を上回ってる場合、エラーを返す
        if (lockedOf(msg.sender, _account_address) < _value) revert();

        // データ更新
        locked[msg.sender][_account_address] = lockedOf(msg.sender, _account_address).sub(_value);
        balances[_receive_address] = balanceOf(_receive_address).add(_value);
        emit Unlock(_account_address, _receive_address, _value);
    }

    // @dev アドレスフォーマット判定
    // @dev アドレスがコントラクトアドレスであるかを判定
    // @param _addr アドレス
    function isContract(address _addr)
        private
        view
        returns (bool is_contract)
    {
        uint256 length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    // @dev EOAへの移転
    // @param _to 宛先アドレス
    // @param _value 移転数量
    function transferToAddress(address _to, uint256 _value, bytes memory /*_data*/)
        private
        returns (bool success)
    {
        // 個人情報登録有無のチェック
        // 取引コントラクトからのtransferと、発行体へのtransferの場合はチェックを行わない。
        if (msg.sender != tradableExchange && _to != owner) {
            require(PersonalInfo(personalInfoAddress).isRegistered(_to, owner) == true);
        }
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // @dev コントラクトアドレスへの移転
    // @param _to 宛先アドレス
    // @param _value 移転数量
    // @param _data 任意のデータ
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

    // @dev トークンの移転
    // @param _to 宛先アドレス
    // @param _value 移転数量
    function transfer(address _to, uint256 _value)
        public
        returns (bool success)
    {
        //  数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();

        // 実行者がtradableExchangeではない場合、譲渡可否のチェックを実施する
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

    // @dev 強制移転
    // @dev オーナーのみ実行可能
    // @param _from 移転元アドレス
    // @param _to 移転先アドレス
    // @param _value 移転数量
    function transferFrom(address _from, address _to, uint256 _value)
        public
        onlyOwner()
        returns (bool success)
    {
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

        emit Transfer(_from, _to, _value);
        return true;
    }

    // @dev 募集申込
    // @param _amount 申込数量
    // @param _data 任意のデータ
    function applyForOffering(uint256 _amount, string memory _data) public {
        // 申込ステータスが停止中の場合、エラーを返す
        require(offeringStatus == true);
        // 個人情報未登録の場合、エラーを返す
        require(PersonalInfo(personalInfoAddress).isRegistered(msg.sender, owner) == true);
        // 募集申込情報を更新
        applications[msg.sender].requestedAmount = _amount;
        applications[msg.sender].data = _data;

        emit ApplyFor(msg.sender, _amount);
    }

    // @dev 追加発行
    // @dev 特定のアドレスの残高に対して、追加発行を行う
    // @dev オーナーのみ実行可能
    // @param _target_address 追加発行対象の残高を保有するアドレス
    // @param _locked_address （任意）資産ロックアドレス
    // @param _amount 追加発行数量
    function issueFrom(address _target_address, address _locked_address, uint256 _amount)
        public
        onlyOwner()
    {
        // locked_addressを指定した場合：ロック資産に対して追加発行を行う
        // locked_addressを指定しない場合：アカウントアドレスの残高に対して追加発行を行う
        if (_locked_address != address(0)) {
            // ロック資産の更新
            locked[_target_address][_locked_address] = lockedOf(_target_address, _locked_address).add(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.add(_amount);
        } else {
            // アカウント残高の更新
            balances[_target_address] = balanceOf(_target_address).add(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.add(_amount);
        }
        emit Issue(msg.sender, _target_address, _locked_address, _amount);
    }

    // @dev 減資
    // @dev 特定のアドレスの残高に対して、発行数量の削減を行う
    // @dev オーナーのみ実行可能
    // @param _target_address 減資対象の残高を保有するアドレス
    // @param _locked_address （任意）資産ロックアドレス
    // @param _amount 削減数量
    function redeemFrom(address _target_address, address _locked_address, uint256 _amount)
        public
        onlyOwner()
    {
        // locked_addressを指定した場合：ロック資産から減資を行う
        // locked_addressを指定しない場合：アカウントアドレスの残高から減資を行う
        if (_locked_address != address(0)) {
            // 減資数量が対象アドレスのロック数量を上回っている場合はエラー
            if (lockedOf(_target_address, _locked_address) < _amount) revert();
            // ロック資産の更新
            locked[_target_address][_locked_address] = lockedOf(_target_address, _locked_address).sub(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.sub(_amount);
        } else {
            // 減資数量が対象アドレスの残高数量を上回っている場合はエラーを返す
            if (balances[_target_address] < _amount) revert();
            // アカウント残高の更新
            balances[_target_address] = balanceOf(_target_address).sub(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.sub(_amount);
        }
        emit Redeem(msg.sender, _target_address, _locked_address, _amount);
    }
}