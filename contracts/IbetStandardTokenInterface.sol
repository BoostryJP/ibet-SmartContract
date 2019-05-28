pragma solidity ^0.4.24;

contract IbetStandardTokenInterface {

  // 基本属性情報
  address public owner; // オーナーのアドレス
  string public name; // 名称
  string public symbol; //略称
  uint8 public constant decimals = 0;
  uint256 public totalSupply; //総発行量
  address public tradableExchange; // 取引可能Exchangeアドレス
  string public contactInformation; // 発行体の問い合わせ先情報
  string public privacyPolicy;  // プライバシーポリシー

  function balanceOf(address _owner) public view returns (uint256);
  function setTradableExchange(address _exchange) public;
  function setContactInformation(string _contactInformation) public;
  function setPrivatePolicy(string _privacyPolicy) public;
  function transfer(address _to, uint _value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}
