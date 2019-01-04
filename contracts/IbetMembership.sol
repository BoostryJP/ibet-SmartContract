pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./ContractReceiver.sol";
import "./IbetStandardTokenInterface.sol";

contract IbetMembership is Ownable, IbetStandardTokenInterface {
  using SafeMath for uint256;

  // 属性情報
  string public details; // 会員権詳細
  string public returnDetails; // リターン詳細
  string public expirationDate; // 有効期限
  string public memo; //メモ欄
  bool public transferable; // 譲渡可能
  bool public status; // 取扱ステータス(True：有効、False：無効)
  bool public initialOfferingStatus; // 新規募集ステータス（True：募集中、False：停止中）

  // 残高数量
  // account_address => balance
  mapping (address => uint256) public balances;

  // 商品画像
  // image class => url
  mapping (uint8 => string) public image_urls;

  // 募集申込
  // account_address => data
  mapping (address => string) public applications;

  // イベント：振替
  event Transfer(address indexed from, address indexed to, uint256 value);

  // イベント：ステータス変更
  event ChangeStatus(bool indexed status);

  // イベント：募集申込
  event ApplyFor(address indexed accountAddress);

  // コンストラクタ
  constructor(string _name, string _symbol,
    uint256 _initialSupply, address _tradableExchange,
    string _details, string _returnDetails,
    string _expirationDate, string _memo,
    bool _transferable)
    public
  {
    owner = msg.sender;
    name = _name;
    symbol = _symbol;
    totalSupply = _initialSupply;
    tradableExchange = _tradableExchange;
    details = _details;
    returnDetails = _returnDetails;
    expirationDate = _expirationDate;
    memo = _memo;
    balances[owner] = totalSupply;
    transferable = _transferable;
    status = true;
  }

  // ファンクション：アドレスフォーマットがコントラクトのものかを判断する
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

  // ファンクション：アドレスへの振替
  function transferToAddress(address _to, uint _value, bytes /*_data*/)
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
  function transferToContract(address _to, uint _value, bytes _data)
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
    returns (bool)
  {
    //  数量が残高を超えている場合、エラーを返す
    if (balanceOf(msg.sender) < _value) revert();
    if (msg.sender != tradableExchange) {
      // 譲渡可能ではない場合、エラーを返す
      require(transferable == true);
    }

    bytes memory empty;
    if(isContract(_to)) {
      return transferToContract(_to, _value, empty);
    } else {
      return transferToAddress(_to, _value, empty);
    }
  }

  // ファンクション：トークンの移転
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
      receiver.tokenFallback(_from, _value, empty);
    } else { // 送信先アドレスがアカウントアドレスの場合
      balances[_from] = balanceOf(_from).sub(_value);
      balances[_to] = balanceOf(_to).add(_value);
    }

    return true;
  }

  // ファンクション：残高確認
  function balanceOf(address _owner)
    public
    view
    returns (uint256)
  {
    return balances[_owner];
  }

  // ファンクション：取引可能Exchangeの更新
  function setTradableExchange(address _exchange)
    public
    onlyOwner()
  {
    tradableExchange = _exchange;
  }

  // ファンクション：会員権詳細更新
  // オーナーのみ実行可能
  function setDetails(string _details)
    public
    onlyOwner()
  {
    details = _details;
  }

  // ファンクション：リターン詳細更新
  // オーナーのみ実行可能
  function setReturnDetails(string _returnDetails)
    public
    onlyOwner()
  {
    returnDetails = _returnDetails;
  }

  // ファンクション：有効期限更新
  // オーナーのみ実行可能
  function setExpirationDate(string _expirationDate)
    public
    onlyOwner()
  {
    expirationDate = _expirationDate;
  }

  // ファンクション：メモ欄更新
  // オーナーのみ実行可能
  function setMemo(string _memo)
    public
    onlyOwner()
  {
    memo = _memo;
  }

  // ファンクション：譲渡可能更新
  // オーナーのみ実行可能
  function setTransferable(bool _transferable)
    public
    onlyOwner()
  {
    transferable = _transferable;
  }

  // ファンクション：取扱ステータス更新
  // オーナーのみ実行可能
  function setStatus(bool _status)
    public
    onlyOwner()
  {
    status = _status;
    emit ChangeStatus(status);
  }

  // ファンクション：商品画像更新
  // オーナーのみ実行可能
  function setImageURL(uint8 _class, string _image_url)
    public
    onlyOwner()
  {
    image_urls[_class] = _image_url;
  }

  // ファンクション：商品の画像を取得する
  function getImageURL(uint8 _class)
    public
    view
    returns (string)
  {
    return image_urls[_class];
  }

  // ファンクション：追加発行
  // オーナーのみ実行可能
  function issue(uint _value)
    public
    onlyOwner()
  {
    totalSupply = totalSupply.add(_value);
    balances[owner] = balanceOf(owner).add(_value);
  }

  // ファンクション：新規募集ステータス更新
  // オーナーのみ実行可能
  function setInitialOfferingStatus(bool _status)
    public
    onlyOwner()
  {
    initialOfferingStatus = _status;
  }

  // ファンクション：募集申込
  function applyForOffering(string _data)
    public
  {
    // 申込ステータスが停止中の場合、エラーを返す
    require(initialOfferingStatus == true);
    applications[msg.sender] = _data;
    emit ApplyFor(msg.sender);
  }

}
