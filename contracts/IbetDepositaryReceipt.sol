pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";
import "./IbetStandardTokenInterface.sol";

contract IbetDepositaryReceipt is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint;

    // 商品固有属性
    string public details; // 詳細
    string public memo; // メモ欄（自由項目）
    bool public status; // 取扱ステータス(True：有効、False：無効)

    // 残高数量
    // account_address => balance
    mapping (address => uint256) public balances;

    // 商品画像
    // image class => url
    mapping (uint8 => string) public image_urls;


    // ---------------------------------------------------------------
    // Event
    // ---------------------------------------------------------------

    // Event：振替
    event Transfer(address indexed from, address indexed to, uint value);

    // Event：ステータス変更
    event ChangeStatus(bool indexed status);


    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    constructor(string memory _name, string memory _symbol,
        uint256 _totalSupply, address _tradableExchange,
        string memory _details, string memory _memo,
        string _contactInformation, string _privacyPolicy)
        public
    {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        tradableExchange = _tradableExchange;
        details = _details;
        memo = _memo;
        balances[owner] = totalSupply;
        status = true;
        contactInformation = _contactInformation;
        privacyPolicy = _privacyPolicy;
    }


    // ---------------------------------------------------------------
    // Function
    // ---------------------------------------------------------------

    // Function：アドレスフォーマットがコントラクトアドレスかを判断する
    function isContract(address _addr)
        private
        view
        returns (bool is_contract)
    {
        uint length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length>0);
    }

    // Function：アカウントアドレスへの振替
    function transferToAddress(address _to, uint _value, bytes memory /*_data*/)
        private
        returns (bool success)
    {
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // Function：コントラクトアドレスへの振替
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

    // Function：クーポンを譲渡する
    function transfer(address _to, uint _value)
        public
        returns (bool success)
    {
        // 譲渡しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        bytes memory empty;
        if(isContract(_to)) {
            return transferToContract(_to, _value, empty);
        } else {
            return transferToAddress(_to, _value, empty);
        }
    }

    // Function：トークンの移転
    // オーナーのみ実行可能
    function transferFrom(address _from, address _to, uint _value)
        public
        onlyOwner()
        returns (bool)
    {
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

        emit Transfer(_from, _to, _value);
        return true;
    }

    // Function：追加発行
    // オーナーのみ実行可能
    function issue(uint _value)
        public
        onlyOwner()
    {
        totalSupply = totalSupply.add(_value);
        balances[owner] = balanceOf(owner).add(_value);
    }

    // Function：焼却（Burn）
    // オーナーのみ実行可能
    function burn(address _address, uint _value)
        public
        onlyOwner()
    {
        //  数量が送信元アドレス（_address）の残高を超えている場合、エラーを返す
        if (balanceOf(_address) < _value) revert();
        totalSupply = totalSupply.sub(_value);
        balances[_address] = balanceOf(_address).sub(_value);
    }

    // Function：残高確認
    function balanceOf(address _owner)
        public
        view
        returns (uint256)
    {
        return balances[_owner];
    }

    // Function：取引可能Exchangeの更新
    function setTradableExchange(address _exchange)
        public
        onlyOwner()
    {
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
    function setPrivacyPolicy(string _privacyPolicy)
        public
        onlyOwner()
    {
        privacyPolicy = _privacyPolicy;
    }

    // Function：詳細を更新する
    // オーナーのみ実行可能
    function setDetails(string memory _details)
        public
        onlyOwner()
    {
        details = _details;
    }

    // Function：メモ欄を更新する
    // オーナーのみ実行可能
    function setMemo(string memory _memo)
        public
        onlyOwner()
    {
        memo = _memo;
    }

    // Function：ステータス（有効・無効）を更新する
    // オーナーのみ実行可能
    function setStatus(bool _status)
        public
        onlyOwner()
    {
        status = _status;
        emit ChangeStatus(status);
    }

    // Function：商品の画像を設定する
    // オーナーのみ実行可能
    function setImageURL(uint8 _class, string memory _image_url)
        public
        onlyOwner()
    {
        image_urls[_class] = _image_url;
    }

    // Function：商品の画像を取得する
    function getImageURL(uint8 _class)
        public
        view
        returns (string memory)
    {
        return image_urls[_class];
    }

}
