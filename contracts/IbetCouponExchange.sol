pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./IbetCoupon.sol";

contract IbetCouponExchange is Ownable {
    using SafeMath for uint256;

    // 残高数量
    // account => token => balance
    mapping(address => mapping(address => uint)) public balances;

    // イベント：全引き出し
    event Withdrawal(address indexed tokenAddress, address indexed accountAddress);

    // イベント：送信
    event Transfer(address indexed tokenAddress, address indexed from, address indexed to, uint256 value);

    // コンストラクタ
    constructor() public {
    }

    // ファンクション：クーポントークンを送信する
    function transfer(address _token, address _to, uint _value) public returns (bool) {
        // <CHK>
        // 1) 送信数量が0の場合
        // 2) 残高数量が送信数量に満たない場合
        // -> 更新処理：全ての残高をsenderのアカウントに戻し、falseを返す
        if (_value == 0 ||
            balances[msg.sender][_token] < _value) {
            IbetCoupon(_token).transfer(msg.sender,balances[msg.sender][_token]);
            balances[msg.sender][_token] = 0;
            return false;
        }
        // 送信
        balances[msg.sender][_token] = balances[msg.sender][_token].sub(_value);
        IbetCoupon(_token).transfer(_to, _value);
        // イベント登録
        emit Transfer(_token, msg.sender, _to, _value);

        return true;
    }

    // ファンクション：全ての残高を引き出しする
    function withdrawAll(address _token) public returns (bool) {
        // <CHK>残高がゼロの場合、REVERT
        if (balances[msg.sender][_token] == 0 ) { revert(); }

        IbetCoupon(_token).transfer(msg.sender,balances[msg.sender][_token]);
        balances[msg.sender][_token] = 0;

        emit Withdrawal(_token, msg.sender);

        return true;
    }

    // ERC223 token deposit handler
    function tokenFallback(address _from, uint _value, bytes /*_data*/) public{
        balances[_from][msg.sender] = balances[_from][msg.sender].add(_value);
    }
}
