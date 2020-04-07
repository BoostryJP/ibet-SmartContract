pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";
import "./IbetStandardTokenInterface.sol";
import "./PersonalInfo.sol";


contract IbetBeneficarySecurity is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint256;

    // 関連アドレス情報
    address public personalInfoAddress; // 個人情報記帳コントラクト

    // 属性情報
    uint256 public unitPrice; // 単価
    uint256 public dividendYield; // 配当利回り
    string public divindendDate; // 配当基準日（JSON）
    string public returnContents; // リターン内容
    string public returnDate; // リターン実施日
    string public cansellationDate; // 消却日
    mapping(uint8 => string) public referenceUrls; // 関連URL
    string public memo; // 補足情報

    // 状態を示す属性
    bool public transferable; // 譲渡可能
    bool public offeringStatus; // 募集ステータス（True：募集中、False：停止中）

    // 残高数量 account_address => balance
    mapping(address => uint256) public balances;

    // 募集申込情報
    struct Application {
        uint256 requestedAmount; // 申込数量
        string data; // その他データ
    }
    // 募集申込 account_address => data
    mapping(address => Application) public applications;

    // イベント：振替
    event Transfer(address indexed from, address indexed to, uint256 value);

    // イベント：ステータス変更
    event ChangeStatus(bool indexed status);

    // イベント：募集ステータス変更
    event ChangeOfferingStatus(bool indexed status);

    // イベント：募集申込
    event ApplyFor(address indexed accountAddress, uint256 amount);

    // コンストラクタ
    constructor(
        string memory _name,
        string memory _symbol,
        address _tradableExchange,
        address _personalInfoAddress,
        uint256 _unitPrice,
        uint256 _totalSupply,
        uint256 _dividendYield,
        string memory _divindendDate,
        string memory _returnDate,
        string memory _returnContents,
        string memory _cansellationDate,
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
        unitPrice = _unitPrice;
        totalSupply = _totalSupply;
        dividendYield = _dividendYield;
        divindendDate = _divindendDate;
        returnContents = _returnContents;
        returnDate = _returnDate;
        cansellationDate = _cansellationDate;
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

    // ファンクション：配当利回りの更新
    // オーナーのみ実行可能
    function setDividendYield(uint256 _dividendYield) public onlyOwner() {
        dividendYield = _dividendYield;
    }

    // ファンクション：配当基準日の更新
    // オーナーのみ実行可能
    function setDivindendDate(string _divindendDate) public onlyOwner() {
        divindendDate = _ddivindendDate;
    }

    // ファンクション：リターン内容の更新
    // オーナーのみ実行可能
    function setReturnContents(string _returnContents) public onlyOwner() {
        returnContents = _returnContents;
    }

    // ファンクション：リターン日の更新
    // オーナーのみ実行可能
    function setReturnDate(string _returnDate) public onlyOwner() {
        returnDate = _returnDate;
    }

    // ファンクション：消却日の更新
    // オーナーのみ実行可能
    function setCansellationDate(string _cansellationDate) public onlyOwner() {
        cansellationDate = _cansellationDate;
    }

    // ファンクション：商品の関連URLを設定する
    // オーナーのみ実行可能
    function setReferenceUrls(uint8 _class, string memory _reference_url)
        public
        onlyOwner()
    {
        reference_urls[_class] = _reference_url;
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
        if (msg.sender != tradableExchange) {
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
    function issue(uint256 _value) public onlyOwner() {
        totalSupply = totalSupply.add(_value);
        balances[owner] = balanceOf(owner).add(_value);
    }
}
