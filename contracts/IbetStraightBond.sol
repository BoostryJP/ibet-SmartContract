pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";
import "./IbetStandardTokenInterface.sol";

contract IbetStraightBond is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint256;

    // 属性情報
    uint256 public faceValue; // 額面
    uint256 public interestRate; // 金利
    string public interestPaymentDate; // 利払日（JSON）
    string public redemptionDate; // 償還日
    uint256 public redemptionAmount; // 償還金額
    string public returnDate; // リターン実施日
    string public returnAmount; // リターン内容
    string public purpose; // 発行目的
    string public memo; //メモ欄
    bool public status; // 取扱ステータス(True：有効、False：無効)

    // 償還状況
    bool public isRedeemed;

    // 残高数量
    // account_address => balance
    mapping (address => uint256) public balances;

    // 第三者認定情報
    // signer_address => status
    mapping (address => uint8) public signatures;

    // 商品画像
    // image class => url
    mapping (uint8 => string) public image_urls;

    // イベント：振替
    event Transfer(address indexed from, address indexed to, uint256 value);

    // イベント：認定
    event Sign(address indexed signer);

    // イベント：認定取消
    event Unsign(address indexed signer);

    // イベント：償還
    event Redeem();

    // イベント：ステータス変更
    event ChangeStatus(bool indexed status);

    // コンストラクタ
    constructor(string memory _name, string memory _symbol,
        uint256 _totalSupply, address _tradableExchange,
        uint256 _faceValue, uint256 _interestRate, string memory _interestPaymentDate,
        string memory _redemptionDate, uint256 _redemptionAmount,
        string memory _returnDate, string memory _returnAmount,
        string memory _purpose, string memory _memo,
        string _contactInformation, string _privacyPolicy)
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
        redemptionAmount = _redemptionAmount;
        returnDate = _returnDate;
        returnAmount = _returnAmount;
        purpose = _purpose;
        memo = _memo;
        balances[owner] = totalSupply;
        isRedeemed = false;
        contactInformation = _contactInformation;
        privacyPolicy = _privacyPolicy;
    }

    // ファンクション：アドレスフォーマットがコントラクトのものかを判断する
    function isContract(address _addr) private view returns (bool is_contract) {
        uint length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length>0);
    }

    // ファンクション：アドレスへの振替
    function transferToAddress(address _to, uint _value, bytes memory /*_data*/)
        private
        returns (bool success)
    {
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    // ファンクション：コントラクトへの振替
    function transferToContract(address _to, uint _value, bytes memory _data)
        private
        returns (bool success)
    {
        require(_to == tradableExchange);
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);

        return true;
    }

    // ファンクション：トークンの送信
    function transfer(address _to, uint _value)
        public
        returns (bool success)
    {
        // <CHK>
        //  数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();

        bytes memory empty;
        if(isContract(_to)) {
            return transferToContract(_to, _value, empty);
        } else {
            return transferToAddress(_to, _value, empty);
        }
    }

    // ファンクション：トークンの移転
    // トークンオーナーのみ実施可
    function transferFrom(address _from, address _to, uint _value)
        public
        onlyOwner()
        returns (bool success)
    {
        // <CHK>
        //  数量が送信元アドレス（from）の残高を超えている場合、エラーを返す
        if (balanceOf(_from) < _value) revert();

        bytes memory empty;

        if(isContract(_to)) { // 送信先アドレスがコントラクトアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
            ContractReceiver receiver = ContractReceiver(_to);
            receiver.tokenFallback(msg.sender, _value, empty);
        } else { // 送信先アドレスがアカウントアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
        }

        return true;
    }

    // ファンクション：残高確認
    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }

    // ファンクション：取引可能Exchangeの更新
    function setTradableExchange(address _exchange) public onlyOwner() {
        tradableExchange = _exchange;
    }

    // ファンクション：問い合わせ先情報更新
    function setContactInformation(string _contactInformation)
        public
        onlyOwner()
    {
        contactInformation = _contactInformation;
    }

    // ファンクション：プライバシーポリシー更新
    function setPrivatePolicy(string _privacyPolicy)
        public
        onlyOwner()
    {
        privacyPolicy = _privacyPolicy;
    }

    // ファンクション：商品の認定をリクエストする
    function requestSignature(address _signer) public returns (bool) {
        signatures[_signer] = 1;
        return true;
    }

    // ファンクション：商品を認定する
    function sign() public returns (bool) {
        require(signatures[msg.sender] == 1);
        signatures[msg.sender] = 2;
        emit Sign(msg.sender);
        return true;
    }

    // ファンクション：商品の認定を取り消す
    function unsign() public returns (bool)  {
        require(signatures[msg.sender] == 2);
        signatures[msg.sender] = 0;
        emit Unsign(msg.sender);
        return true;
    }

    // ファンクション：償還する
    function redeem() public onlyOwner() {
        isRedeemed = true;
        emit Redeem();
    }

    // ファンクション：商品の画像を設定する
    function setImageURL(uint8 _class, string memory _image_url) public onlyOwner() {
        image_urls[_class] = _image_url;
    }

    // ファンクション：商品の画像を取得する
    function getImageURL(uint8 _class) public view returns (string memory) {
        return image_urls[_class];
    }

    // ファンクション：メモ欄を更新する
    function updateMemo(string memory _memo) public onlyOwner() {
        memo = _memo;
    }

    // ファンクション：ステータスの有効・無効を更新する
    // オーナーのみ実行可能
    function setStatus(bool _status) public onlyOwner() {
        status = _status;
        emit ChangeStatus(status);
    }

}
