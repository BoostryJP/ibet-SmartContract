pragma solidity ^0.4.24;

contract ExchangeStorageModel {
    struct OTCOrder {
        address owner;
        address counterpart;
        address token;
        uint256 amount; // 数量
        uint256 price; // 価格
        address agent; // 決済業者のアドレス
        bool canceled; // キャンセル済みフラグ
    }
    struct OTCAgreement {
        address counterpart; // 約定相手
        uint256 amount; // 約定数量
        uint256 price; // 約定価格
        bool canceled; // キャンセル済みフラグ
        bool paid; // 支払い済みフラグ
        uint256 expiry; // 有効期限（約定から１４日）
    }
    function mappingOTCOrder(
        address _owner,
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent,
        bool _canceled
    )
        internal
        returns (OTCOrder)
    {
        OTCOrder memory _order = OTCOrder(_owner, _counterpart, _token, _amount, _price, _agent, _canceled);
        return _order;
    }

    function mappingOTCAgreement(
        address _counterpart,
        uint256 _amount,
        uint256 _price,
        bool _canceled,
        bool _paid,
        uint256 _expiry
    )
        internal
        returns (OTCAgreement)
    {
        OTCAgreement memory _agreement = OTCAgreement(_counterpart, _amount, _price, _canceled, _paid, _expiry);
        return _agreement;
    }
}