pragma solidity ^0.4.24;

contract IbetStandardTokenInterface {
  // 基本属性情報
  address public owner;
  string public name;
  string public symbol;
  uint8 public constant decimals = 0;
  uint256 public totalSupply;
  address public tradableExchange;

  function balanceOf(address _owner) public view returns (uint256);
  function setTradableExchange(address _exchange) public;
  function transfer(address _to, uint _value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}
