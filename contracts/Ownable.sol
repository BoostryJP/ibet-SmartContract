pragma solidity ^0.4.24;


/// @title Ownership Management Contract
contract Ownable {
    /// オーナーアドレス
    address public owner;

    /// イベント：オーナー変更
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /// [CONSTRUCTOR]
    constructor() public {
        owner = msg.sender;
    }

    /// @notice オーナー権限チェック
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    /// @notice オーナー変更
    /// @dev オーナーのみ実行可能
    /// @param newOwner 新しいオーナー
    function transferOwnership(address newOwner)
        public
        onlyOwner
    {
        require(newOwner != address(0));
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

}
