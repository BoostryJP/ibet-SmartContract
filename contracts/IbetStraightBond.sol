pragma solidity ^0.4.19;

import "./SafeMath.sol";
import "./Ownable.sol";

contract IbetStraightBond is Ownable {
    using SafeMath for uint256;

    address public owner;
    string public name;
    string public symbol;
    uint256 public constant decimals = 0;
    uint256 public totalSupply;
    bool isRedeemed;
    uint8 public productType; //商品区分
    uint8 public faceValue; //額面
    uint8 public interestRate; //金利
    uint256 public interestPaymentDate1; //利払日１
    uint256 public interestPaymentDate2; //利払日２
    uint256 public redemptionDate; //償還日
    uint256 public redemptionAmount; //償還金額
    string public purpose; //発行目的
    string returnAmount; //リターン
    uint256 returnDate; //リターン実施日

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
    mapping (address => mapping (address => uint256)) public allowed;

    function IbetStraightBond(string _name, string _symbol, uint256 _totalSupply) public {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        balances[owner].balance = totalSupply;
        num_holders = 1;
        isRedeemed = false;
    }

    function transfer(address _to, uint256 _value) public returns (bool) {
        require(_to != address(0));
        require(_value <= balances[msg.sender].balance);

        balances[msg.sender].balance = balances[msg.sender].balance.sub(_value);
        balances[_to].balance = balances[_to].balance.add(_value);

        if(!balances[_to].isValue) {
            holders[num_holders] = _to;
            num_holders = num_holders + 1;
        }

        Transfer(msg.sender, _to, _value);
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
}
