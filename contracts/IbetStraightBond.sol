pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";

contract IbetStraightBond is Ownable {
    using SafeMath for uint256;

    // 属性情報
    address public owner;
    string public name;
    string public symbol;
    uint256 public constant decimals = 0;
    uint256 public totalSupply; // 総発行量
    uint256 public faceValue; // 額面
    uint256 public interestRate; // 金利
    string public interestPaymentDate; // 利払日（JSON）
    string public redemptionDate; // 償還日
    uint256 public redemptionAmount; // 償還金額
    string public returnDate; // リターン実施日
    string public returnAmount; // リターン内容
    string public purpose; // 発行目的
    string public memo; //メモ欄

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

    // コンストラクタ
    constructor(string _name, string _symbol, uint256 _totalSupply,
        uint256 _faceValue, uint256 _interestRate, string _interestPaymentDate,
        string _redemptionDate, uint256 _redemptionAmount,
        string _returnDate, string _returnAmount,
        string _purpose, string _memo) public {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
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
    }

    // ファンクション：トークンを振替する
    function transfer(address _to, uint _value) public returns (bool success) {
        bytes memory empty;
        if(isContract(_to)) {
            return transferToContract(_to, _value, empty);
        }
        else {
            return transferToAddress(_to, _value, empty);
        }
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
    function transferToAddress(address _to, uint _value, bytes /*_data*/) private returns (bool success) {
        // 振替しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        // 償還済みの場合、エラーを返す
        if (isRedeemed == true) revert();

        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    // ファンクション：コントラクトへの振替
    function transferToContract(address _to, uint _value, bytes _data) private returns (bool success) {
        // 振替しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        // 償還済みの場合、エラーを返す
        if (isRedeemed == true) revert();

        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);
        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);
        return true;
    }

    // ファンクション：残高確認
    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
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
    function setImageURL(uint8 _class, string _image_url) public onlyOwner() {
        image_urls[_class] = _image_url;
    }

    // ファンクション：商品の画像を取得する
    function getImageURL(uint8 _class) public view returns (string) {
        return image_urls[_class];
    }

    // メモ欄を更新する
    function updateMemo(string _memo) public onlyOwner() {
        memo = _memo;
    }

}
