pragma solidity ^0.4.19;

import "./SafeMath.sol";
import "./Ownable.sol";

contract ContractReceiver {
  function tokenFallback(address _from, uint _value, bytes _data) public;
}

contract IbetStraightBond is Ownable {
    using SafeMath for uint256;

    address public owner;
    string public name;
    string public symbol;
    uint256 public constant decimals = 0;
    uint256 public totalSupply; //総発行量
    uint256 public faceValue; //額面
    uint256 public interestRate; //金利
    string public interestPaymentDate1; //利払日１
    string public interestPaymentDate2; //利払日２
    string public redemptionDate; //償還日
    uint256 public redemptionAmount; //償還金額
    string public returnAmount; //リターン内容
    string public returnDate; //リターン実施日
    string public purpose; //発行目的

    bool public isRedeemed; //償還状況

    struct balance {
        uint256 balance;
        bool isValue;
    }

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Sign(address signer);
    event Unsign(address signer);
    event Redeem();

    uint256 public num_holders;
    mapping (uint256 => address) public holders;
    mapping (address => balance) public balances;
    mapping (address => uint8) public signatures;
    mapping (uint8 => string) public image_urls;

    function IbetStraightBond(string _name, string _symbol, uint256 _totalSupply, uint256 _faceValue,
        uint256 _interestRate, string _interestPaymentDate1, string _interestPaymentDate2,
        string _redemptionDate, uint256 _redemptionAmount,
        string _returnDate, string _returnAmount, string _purpose) public {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        faceValue = _faceValue;
        interestRate = _interestRate;
        interestPaymentDate1 = _interestPaymentDate1;
        interestPaymentDate2 = _interestPaymentDate2;
        redemptionDate = _redemptionDate;
        redemptionAmount = _redemptionAmount;
        returnDate = _returnDate;
        returnAmount = _returnAmount;
        purpose = _purpose;
        balances[owner].balance = totalSupply;
        num_holders = 1;
        isRedeemed = false;
    }

    // Standard function transfer similar to ERC20 transfer with no _data .
    // Added due to backwards compatibility reasons .
    function transfer(address _to, uint _value) public returns (bool success) {

        //standard function transfer similar to ERC20 transfer with no _data
        //added due to backwards compatibility reasons
        bytes memory empty;
        if(isContract(_to)) {
            return transferToContract(_to, _value, empty);
        }
        else {
            return transferToAddress(_to, _value, empty);
        }
    }

    //assemble the given address bytecode. If bytecode exists then the _addr is a contract.
    function isContract(address _addr) private view returns (bool is_contract) {
        uint length;
        assembly {
            //retrieve the size of the code on target address, this needs assembly
            length := extcodesize(_addr)
        }
        return (length>0);
    }

    //function that is called when transaction target is an address
    function transferToAddress(address _to, uint _value, bytes /*_data*/) private returns (bool success) {
        if (balanceOf(msg.sender) < _value) revert();
        balances[msg.sender].balance = balanceOf(msg.sender).sub(_value);
        balances[_to].balance = balanceOf(_to).add(_value);
        return true;
    }

    //function that is called when transaction target is a contract
    function transferToContract(address _to, uint _value, bytes _data) private returns (bool success) {
        if (balanceOf(msg.sender) < _value) revert();
        balances[msg.sender].balance = balanceOf(msg.sender).sub(_value);
        balances[_to].balance = balanceOf(_to).add(_value);
        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);
        return true;
    }

    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner].balance;
    }

    function requestSignature(address _signer) public returns (bool) {
        signatures[_signer] = 1;
        return true;
    }

    function sign() public returns (bool) {
        require(signatures[msg.sender] == 1);
        signatures[msg.sender] = 2;
        Sign(msg.sender);
        return true;
    }

    function unsign() public returns (bool)  {
        require(signatures[msg.sender] == 2);
        signatures[msg.sender] = 0;
        Unsign(msg.sender);
        return true;
    }

    function redeem() public onlyOwner() {
        isRedeemed = true;
        Redeem();
    }

    function isSigned(address _signer) public constant returns (uint8) {
        return signatures[_signer];
    }

    function holderAt(uint256 _index) public constant returns (address) {
        return holders[_index];
    }

    function setImageURL(uint8 _class, string _image_url) public onlyOwner() {
        image_urls[_class] = _image_url;
    }

    function getImageURL(uint8 _class) public view returns (string) {
        return image_urls[_class];
    }

}
