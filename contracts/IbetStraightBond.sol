pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./PersonalInfo.sol";
import "../interfaces/ContractReceiver.sol";
import "../interfaces/IbetStandardTokenInterface.sol";

/// @title ibet Straight Bond Token
contract IbetStraightBond is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint256;

    /// 属性情報
    uint256 public faceValue; // 額面
    uint256 public interestRate; // 年利
    string public interestPaymentDate; // 利払日（JSON）
    string public redemptionDate; // 償還日
    uint256 public redemptionValue; // 償還金額
    string public returnDate; // 特典付与日
    string public returnAmount; // 特典内容
    string public purpose; // 発行目的
    string public memo; // 補足情報
    bool public status; // 取扱ステータス(True：有効、False：無効)
    bool public initialOfferingStatus; // 新規募集ステータス（True：募集中、False：停止中）

    /// 募集申込情報
    struct Application {
        uint256 requestedAmount; // 申込数量
        uint256 allottedAmount; // 割当数量
        string data; // その他データ
    }

    /// 償還状況
    bool public isRedeemed;

    /// 譲渡可否
    bool public transferable;

    /// 個人情報記帳コントラクト
    address public personalInfoAddress;

    /// 残高数量
    /// account_address => balance
    mapping(address => uint256) public balances;

    /// 第三者認定情報
    /// signer_address => status
    mapping(address => uint8) public signatures;

    /// 商品画像
    /// image class => url
    mapping(uint8 => string) public image_urls;

    /// 募集申込
    /// account_address => data
    mapping(address => Application) public applications;

    /// イベント：移転
    event Transfer(address indexed from, address indexed to, uint256 value);

    /// イベント：認定
    event Sign(address indexed signer);

    /// イベント：認定取消
    event Unsign(address indexed signer);

    /// イベント：償還
    event Redeem();

    /// イベント：ステータス変更
    event ChangeStatus(bool indexed status);

    /// イベント：募集ステータス変更
    event ChangeInitialOfferingStatus(bool indexed status);

    /// イベント：募集申込
    event ApplyFor(address indexed accountAddress, uint256 amount);

    /// イベント：割当
    event Allot(address indexed accountAddress, uint256 amuont);

    /// [CONSTRUCTOR]
    /// @param _name 名称
    /// @param _symbol 略称
    /// @param _totalSupply 総発行数量
    /// @param _tradableExchange 取引コントラクト
    /// @param _faceValue 額面
    /// @param _interestRate 年利
    /// @param _interestPaymentDate 利払日
    /// @param _redemptionDate 償還日
    /// @param _redemptionValue 償還金額
    /// @param _returnDate 特典付与日
    /// @param _returnAmount 特典内容
    /// @param _purpose 発行目的
    /// @param _memo 補足情報
    /// @param _contactInformation 問い合わせ先情報
    /// @param _privacyPolicy プライバシーポリシー
    /// @param _personalInfoAddress 個人情報コントラクトアドレス
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _totalSupply,
        address _tradableExchange,
        uint256 _faceValue,
        uint256 _interestRate,
        string memory _interestPaymentDate,
        string memory _redemptionDate,
        uint256 _redemptionValue,
        string memory _returnDate,
        string memory _returnAmount,
        string memory _purpose,
        string memory _memo,
        string _contactInformation,
        string _privacyPolicy,
        address _personalInfoAddress
    )
        public
    {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        tradableExchange = _tradableExchange;
        faceValue = _faceValue;
        interestRate = _interestRate;
        interestPaymentDate = _interestPaymentDate;
        redemptionDate = _redemptionDate;
        redemptionValue = _redemptionValue;
        returnDate = _returnDate;
        returnAmount = _returnAmount;
        purpose = _purpose;
        memo = _memo;
        transferable = true;
        balances[owner] = totalSupply;
        isRedeemed = false;
        status = true;
        contactInformation = _contactInformation;
        privacyPolicy = _privacyPolicy;
        personalInfoAddress = _personalInfoAddress;
    }

    /// @notice 追加発行
    /// @dev オーナーのみ実行可能
    /// @param _value 追加発行数量
    function issue(uint _value)
        public
        onlyOwner()
    {
        totalSupply = totalSupply.add(_value);
        balances[owner] = balanceOf(owner).add(_value);
    }

    /// @notice アドレスがコントラクトアドレスであるかを判定
    /// @param _addr アドレス
    /// @return is_contract 判定結果
    function isContract(address _addr)
        private
        view
        returns (bool is_contract)
    {
        uint length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    /// @notice EOAへの移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transferToAddress(address _to, uint _value, bytes memory /*_data*/)
        private
        returns (bool success)
    {
        if (msg.sender != tradableExchange) {
            require(PersonalInfo(personalInfoAddress).isRegistered(_to, owner) == true);
        }
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    /// @notice コントラクトアドレスへの移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @param _data 任意のデータ
    /// @return success 処理結果
    function transferToContract(address _to, uint _value, bytes memory _data)
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

    /// @notice トークンの移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transfer(address _to, uint _value)
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

    /// @notice 強制移転
    /// @dev オーナーのみ実行可能
    /// @param _from 移転元アドレス
    /// @param _to 移転先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transferFrom(address _from, address _to, uint _value)
        public
        onlyOwner()
        returns (bool success)
    {
        // <CHK>
        //  数量が送信元アドレス（from）の残高を超えている場合、エラーを返す
        if (balanceOf(_from) < _value) revert();

        bytes memory empty;

        if (isContract(_to)) {// 送信先アドレスがコントラクトアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
            ContractReceiver receiver = ContractReceiver(_to);
            receiver.tokenFallback(msg.sender, _value, empty);
        } else {// 送信先アドレスがアカウントアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
        }

        // イベント登録
        emit Transfer(_from, _to, _value);

        return true;
    }

    /// @notice 残高の参照
    /// @param _owner 保有者のアドレス
    /// @return 残高数量
    function balanceOf(address _owner)
        public
        view
        returns (uint256)
    {
        return balances[_owner];
    }

    /// @notice 取引コントラクトの更新
    /// @dev オーナーのみ実行可能
    /// @param _exchange 更新後取引コントラクト
    function setTradableExchange(address _exchange)
        public
        onlyOwner()
    {
        tradableExchange = _exchange;
    }

    /// @notice 問い合わせ先情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _contactInformation 問い合わせ先情報
    function setContactInformation(string _contactInformation)
        public
        onlyOwner()
    {
        contactInformation = _contactInformation;
    }

    /// @notice プライバシーポリシーの更新
    /// @dev オーナーのみ実行可能
    /// @param _privacyPolicy プライバシーポリシー
    function setPrivacyPolicy(string _privacyPolicy)
        public
        onlyOwner()
    {
        privacyPolicy = _privacyPolicy;
    }

    /// @notice 商品の認定をリクエストする
    /// @param _signer 認定者
    /// @return 処理結果
    function requestSignature(address _signer)
        public
        returns (bool)
    {
        signatures[_signer] = 1;
        return true;
    }

    /// @notice 商品を認定する
    /// @return 処理結果
    function sign()
        public
        returns (bool)
    {
        require(signatures[msg.sender] == 1);
        signatures[msg.sender] = 2;
        emit Sign(msg.sender);
        return true;
    }

    /// @notice 商品の認定を取り消す
    /// @return 処理結果
    function unsign()
        public
        returns (bool)
    {
        require(signatures[msg.sender] == 2);
        signatures[msg.sender] = 0;
        emit Unsign(msg.sender);
        return true;
    }

    /// @notice 償還する
    /// @dev オーナーのみ実行可能
    function redeem()
        public
        onlyOwner()
    {
        isRedeemed = true;
        emit Redeem();
    }

    /// @notice 商品画像の更新
    /// @dev オーナーのみ実行可能
    /// @param _class 画像番号
    /// @param _image_url 画像URL
    function setImageURL(uint8 _class, string memory _image_url)
        public
        onlyOwner()
    {
        image_urls[_class] = _image_url;
    }

    /// @notice 商品画像の参照
    /// @param _class 画像番号
    /// @return 画像URL
    function getImageURL(uint8 _class)
        public
        view
        returns (string memory)
    {
        return image_urls[_class];
    }

    /// @notice 補足情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _memo 補足情報
    function updateMemo(string memory _memo)
        public
        onlyOwner()
    {
        memo = _memo;
    }

    /// @notice 譲渡可否の更新
    /// @dev オーナーのみ実行可能
    /// @param _transferable 譲渡可否
    function setTransferable(bool _transferable)
        public
        onlyOwner()
    {
        transferable = _transferable;
    }

    /// @notice 取扱ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _status 更新後の取扱ステータス
    function setStatus(bool _status)
        public
        onlyOwner()
    {
        status = _status;
        emit ChangeStatus(status);
    }

    /// @notice 個人情報記帳コントラクトの更新
    /// @dev オーナーのみ実行可能
    /// @param _address 個人情報記帳コントラクトのアドレス
    function setPersonalInfoAddress(address _address)
        public
        onlyOwner()
    {
        personalInfoAddress = _address;
    }

    /// @notice 新規募集ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _status 募集ステータス
    function setInitialOfferingStatus(bool _status)
        public
        onlyOwner()
    {
        initialOfferingStatus = _status;
        emit ChangeInitialOfferingStatus(_status);
    }

    /// @notice 募集申込
    /// @param _data 申込付与情報
    function applyForOffering(uint256 _amount, string memory _data)
        public
    {
        // 申込ステータスが停止中の場合、エラーを返す
        require(initialOfferingStatus == true);

        // 個人情報未登録の場合、エラーを返す
        require(PersonalInfo(personalInfoAddress).isRegistered(msg.sender, owner) == true);

        applications[msg.sender].requestedAmount = _amount;
        applications[msg.sender].data = _data;
        emit ApplyFor(msg.sender, _amount);
    }

    /// @notice 募集割当
    /// @dev オーナーのみ実行可能
    /// @param _address 割当先アドレス
    /// @param _amount 割当数量
    function allot(address _address, uint256 _amount)
        public
        onlyOwner()
    {
        applications[_address].allottedAmount = _amount;
        emit Allot(_address, _amount);
    }

}
