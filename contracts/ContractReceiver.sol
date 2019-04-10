pragma solidity ^0.4.24;

contract ContractReceiver {
  function tokenFallback(address _from, uint _value, bytes memory _data) public;
}
