pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";

contract IbetCoupon is Ownable {
    using SafeMath for uint;

    // 属性情報
    address public owner; // オーナー
    string public name; // クーポン名
    string public symbol; // シンボル
    uint public constant decimals = 0; // 小数点以下桁数
    uint public totalSupply; // 総発行量
    string public details; // クーポン詳細
    string public memo; // メモ欄
    string public expirationDate; // 有効期限
    bool public isValid; // 有効・無効フラグ
    bool public transferable; // 譲渡可能

    // 残高数量
    // account_address => balance
    mapping (address => uint) public balances;

    // 使用済数量
    // account_address => used quantity
    mapping (address => uint) public useds;

    // クーポン画像
    // image class => url
    mapping (uint8 => string) public image_urls;

    // イベント：振替
    event Transfer(address indexed from, address indexed to, uint value);

    // コンストラクタ
    constructor(string _name, string _symbol, uint _totalSupply,
        string _details, string _memo, string _expirationDate,
        bool _transferable) public {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        details = _details;
        memo = _memo;
        expirationDate = _expirationDate;
        balances[owner] = totalSupply;
        isValid = true;
        transferable = _transferable;
    }

    // ファンクション：アドレスフォーマットがコントラクトアドレスかを判断する
    function isContract(address _addr) private view returns (bool is_contract) {
        uint length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length>0);
    }

    // ファンクション：アカウントアドレスへの振替
    function transferToAddress(address _to, uint _value, bytes /*_data*/) private returns (bool success) {
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // ファンクション：コントラクトアドレスへの振替
    function transferToContract(address _to, uint _value, bytes _data) private returns (bool success) {
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);
        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);
        return true;
    }

    // ファンクション：クーポンを割当する
    // オーナーのみ実行可能
    function allocate(address _to, uint _value) public onlyOwner() returns (bool success) {
        // 割当しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        // 無効化されている場合、エラーを返す
        if (isValid == false) revert();

        bytes memory empty;
        if(isContract(_to)) {
            return transferToContract(_to, _value, empty);
        }
        else {
            return transferToAddress(_to, _value, empty);
        }
    }

    // ファンクション：クーポンを譲渡する
    function transfer(address _to, uint _value) public returns (bool success) {
        // 譲渡しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        // 無効化されている場合、エラーを返す
        if (isValid == false) revert();
        // 譲渡可能なクーポンではない場合、エラーを返す
        require(transferable == true);

        bytes memory empty;
        if(isContract(_to)) {
            return transferToContract(_to, _value, empty);
        }
        else {
            return transferToAddress(_to, _value, empty);
        }
    }

    // ファンクション：クーポンの消費
    function consume(uint _value) public {
        // 消費しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        // 無効化されている場合、エラーを返す
        if (isValid == false) revert();

        // 残高数量を更新する
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);

        // 使用済数量を更新する
        useds[msg.sender] = usedOf(msg.sender).add(_value);
    }

    // ファンクション：追加発行
    // オーナーのみ実行可能
    function issue(uint _value) public onlyOwner() {
        totalSupply = totalSupply.add(_value);
        balances[owner] = balanceOf(owner).add(_value);
    }

    // ファンクション：クーポン詳細を更新する
    // オーナーのみ実行可能
    function updateDetails(string _details) public onlyOwner() {
        details = _details;
    }

    // ファンクション：メモ欄を更新する
    // オーナーのみ実行可能
    function updateMemo(string _memo) public onlyOwner() {
        memo = _memo;
    }

    // ファンクション：残高確認
    function balanceOf(address _owner) public view returns (uint) {
        return balances[_owner];
    }

    // ファンクション：使用済数量確認
    function usedOf(address _owner) public view returns (uint) {
        return useds[_owner];
    }

    // ファンクション：商品の画像を設定する
    // オーナーのみ実行可能
    function setImageURL(uint8 _class, string _image_url) public onlyOwner() {
        image_urls[_class] = _image_url;
    }

    // ファンクション：商品の画像を取得する
    function getImageURL(uint8 _class) public view returns (string) {
        return image_urls[_class];
    }

    // ファンクション：クーポンの有効・無効を更新する
    // オーナーのみ実行可能
    function updateStatus(bool _isValid) public onlyOwner() {
        isValid = _isValid;
    }

}