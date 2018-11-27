pragma solidity ^0.4.24;

import "./IbetStandardTokenInterface.sol";
import "./Ownable.sol";

contract TokenList is Ownable {

    struct Token {
        address token_address;
        string token_template;
        address owner_address;
    }

    mapping(address => Token) tokens;
    Token[] token_list;

    event Register(address indexed token_address, string token_template,
        address owner_address);

    function register(address _token_address, string _token_template) public {
        require(tokens[_token_address].token_address == 0);
        require(IbetStandardTokenInterface(_token_address).owner() == msg.sender);
        tokens[_token_address].token_address = _token_address;
        tokens[_token_address].token_template = _token_template;
        tokens[_token_address].owner_address = msg.sender;
        token_list.push(Token({
            token_address: _token_address,
            token_template: _token_template,
            owner_address: msg.sender
        }));
        emit Register(_token_address, _token_template, msg.sender);
    }

    function changeOwner(address _token_address, address _new_owner_address) public {
        require(tokens[_token_address].token_address != 0);
        require(tokens[_token_address].owner_address == msg.sender);
        tokens[_token_address].owner_address = _new_owner_address;
        for (uint i = 0; i < token_list.length; i++) {
            if (token_list[i].token_address == _token_address) {
                token_list[i].owner_address = _new_owner_address;
            }
        }
    }

    function getOwnerAddress(address _token_address) public view
        returns (address issuer_address)
        {
            issuer_address = tokens[_token_address].owner_address;
        }

    function getListLength() public view
        returns (uint length)
        {
            length = token_list.length;
        }

    function getTokenByNum(uint _num) public view
        returns (address token_address, string token_template, address owner_address)
        {
            token_address = token_list[_num].token_address;
            token_template = token_list[_num].token_template;
            owner_address = token_list[_num].owner_address;
        }

    function getTokenByAddress(address _token_address) public view
        returns (address token_address, string token_template, address owner_address)
        {
            token_address = tokens[_token_address].token_address;
            token_template = tokens[_token_address].token_template;
            owner_address = tokens[_token_address].owner_address;
        }

}
