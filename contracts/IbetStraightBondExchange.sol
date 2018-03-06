pragma solidity ^0.4.19;

import "./SafeMath.sol";
import "./IbetStraightBond.sol";

contract IbetStraightBondExchange {
    using SafeMath for uint256;

    // 注文情報
    struct Order {
        address owner;
        address token;
        uint256 amount; // 数量
        uint256 price; // 価格
        bool isBuy; // 売買区分（買い：True）
        address agent; // 決済業者のアドレス
    }
    
    // 約定情報
    struct Agreement {
        address counterpart; // 約定相手
        uint256 amount; // 約定数量
        uint256 price; // 約定価格
        bool canceled; // キャンセル済みフラグ
        bool paid; // 支払い済みフラグ
    }

    // 残高数量
    // account => token => balance
    mapping(address => mapping(address => uint256)) public balances;

    // 拘束数量
    // account => token => order commitment
    mapping(address => mapping(address => uint256)) public commitments;

    // 注文情報
    // orderId => order
    mapping(uint256 => Order) public orderBook;

    // 直近注文ID
    uint256 public latestOrderId = 0;

    // 約定情報
    // orderId => agreementId => Agreement
    mapping(uint256 => mapping(uint256 => Agreement)) public agreements;

    // 直近約定ID
    // orderId => latestAgreementId
    mapping(uint256 => uint256) public latestAgreementIds;

    // 現在値
    // token => latest_price
    mapping(address => uint256) public lastPrice;

    // イベント：注文
    event NewOrder(address indexed tokenAddress, uint256 orderId, address indexed accountAddress, bool indexed isBuy, uint256 price, uint256 amount, address agentAddress);

    // イベント：注文取消
    event CancelOrder(address indexed tokenAddress, uint256 orderId, address indexed accountAddress, bool indexed isBuy, uint256 price, uint256 amount, address agentAddress);

    // イベント：約定
    event Agree(address indexed tokenAddress, uint256 orderId, uint256 agreementId, address indexed buyAddress, address indexed sellAddress, uint256 price, uint256 amount, address agentAddress);

    // イベント：決済OK
    event SettlementOK(address indexed tokenAddress, uint256 orderId, uint256 agreementId, address indexed buyAddress, address indexed sellAddress, uint256 price, uint256 amount, address agentAddress);

    // イベント：決済NG
    event SettlementNG(address indexed tokenAddress, uint256 orderId, uint256 agreementId, address indexed buyAddress, address indexed sellAddress, uint256 price, uint256 amount, address agentAddress);

    // コンストラクタ
    function IbetStraightBondExchange() public {
    }

    // 投資家：新規注文を作成する
    function createOrder(address _token, uint256 _amount, uint256 _price, bool _isBuy, address _agent) public returns (bool) {
        // 注文数量が0の場合、エラーを返す
        if (_amount == 0) { revert(); }
        // 売り注文の場合、残高数量が発注数量に満たない場合、エラーを返す
        if (!_isBuy && balances[msg.sender][_token] < _amount) { revert(); }

        // 注文IDをカウントアップ -> 注文情報を挿入
        uint256 orderId = latestOrderId++;
        orderBook[orderId] = Order(msg.sender, _token, _amount, _price, _isBuy, _agent);

        // 売り注文の場合、預かりを拘束
        if (!_isBuy) {
            balances[msg.sender][_token] = balances[msg.sender][_token].sub(_amount);
            commitments[msg.sender][_token] = balances[msg.sender][_token].add(_amount);
        }

        NewOrder(_token, orderId, msg.sender, _isBuy, _price, _amount, _agent);

        return true;
    }

    // 投資家：注文をキャンセルする
    function cancelOrder(uint256 _orderId) public returns (bool) {
        Order storage order = orderBook[_orderId];
        // 元注文の残注文数量が0の場合、エラーを返す
        if (order.amount == 0) { revert(); }
        // 元注文の発注者と、注文キャンセルの実施者が異なる場合、エラーを返す
        if (msg.sender != order.owner) { revert(); }

        // 売り注文の場合、預かりを解放
        if (!order.isBuy) {
            balances[msg.sender][order.token] = balances[msg.sender][order.token].add(order.amount);
            commitments[msg.sender][order.token] = commitments[msg.sender][order.token].sub(order.amount);
        }

        CancelOrder(order.token, _orderId, msg.sender, order.isBuy, order.price, order.amount, order.agent);

        return true;
    }

    // 投資家：注文に応じる -> 約定
    function executeOrder(uint256 _orderId, uint256 _amount, bool _isBuy) public returns (bool) {
        if (_orderId > latestOrderId) { revert(); }
        Order storage order = orderBook[_orderId];

        // 注文数量が0の場合はエラーを返す
        if (_amount == 0) { revert(); }
        // 数量が元注文の数量を超過している場合、エラーを返す
        if (order.amount < _amount) { revert(); }
        // 元注文の発注者と同一のアドレスからの発注の場合、エラーを返す
        if (msg.sender == order.owner) { revert(); }
        // 発注者（売り注文）の残高が発注数量を下回っている場合、エラーを返す
        if (order.isBuy && balances[msg.sender][order.token] < _amount) { revert(); }
        // 元注文と、発注する注文が同一の売買区分の場合、エラーを返す
        if (order.isBuy == _isBuy) { revert(); }

        // 約定IDをカウントアップ => 約定情報を挿入する
        uint256 latestAgreementId = latestAgreementIds[_orderId]++;
        agreements[_orderId][latestAgreementId] = Agreement(msg.sender, _amount, order.price, false, false);
        // 元注文の数量を減らす
        order.amount = order.amount.sub(_amount);

        if (order.isBuy) {
            // 買い注文に対して売り注文で応じた場合、売りの預かりを拘束
            balances[msg.sender][order.token] = balances[msg.sender][order.token].sub(_amount);
            commitments[msg.sender][order.token] = commitments[msg.sender][order.token].add(_amount);
            // イベント登録：約定
            Agree(order.token, _orderId, latestAgreementId, order.owner, msg.sender, order.price, _amount, order.agent);
        } else {
            // イベント登録：約定
            Agree(order.token, _orderId, latestAgreementId, msg.sender, order.owner, order.price, _amount, order.agent);
        }

        // 現在値を更新する
        lastPrice[order.token] = order.price;

        return true;
    }

    // 決済業者：決済処理 -> 預かりの移動 -> 預かりの引き出し
    function confirmAgreement(uint256 _orderId, uint256 _agreementId) public returns (bool) {
        // 指定した注文番号が、直近の注文IDを上回っている場合、エラーを返す
        if (_orderId > latestOrderId) { revert(); }
        // 指定した約定IDが、直近の約定IDを上回っている場合、エラーを返す
        if (_agreementId > latestAgreementIds[_orderId]) { revert(); }

        Order storage order = orderBook[_orderId];
        Agreement storage agreement = agreements[_orderId][_agreementId];

        // すでに支払い済みの場合、エラーを返す
        if (agreement.paid) { revert(); }
        // 元注文で指定した決済業者とは異なる場合、エラーを返す
        if (msg.sender != order.agent) { revert(); }

        // 支払い済みフラグを支払い済み（True）に更新する
        agreement.paid = true;

        if (order.isBuy) {
            // 買注文の場合、突合相手（売り手）から注文者（買い手）へと資産移転を行う
            commitments[agreement.counterpart][order.token] = commitments[agreement.counterpart][order.token].sub(agreement.amount);
            IbetStraightBond(order.token).transfer(order.owner,agreement.amount);
            SettlementOK(order.token, _orderId, _agreementId, order.owner, agreement.counterpart, order.price, agreement.amount, order.agent);
        } else {
            // 売注文の場合、注文者（売り手）から突合相手（買い手）へと資産移転を行う
            commitments[order.owner][order.token] = commitments[order.owner][order.token].sub(agreement.amount);
            IbetStraightBond(order.token).transfer(agreement.counterpart,agreement.amount);
            SettlementOK(order.token, _orderId, _agreementId, agreement.counterpart, order.owner, order.price, agreement.amount, order.agent);
        }

        return true;
    }

    // 決済業者：約定キャンセル
    function cancelAgreement(uint256 _orderId, uint256 _agreementId) public returns (bool) {
        // 指定した注文番号が、直近の注文IDを上回っている場合、エラーを返す
        if (_orderId > latestOrderId) { revert(); }
        // 指定した約定IDが、直近の約定IDを上回っている場合、エラーを返す
        if (_agreementId > latestAgreementIds[_orderId]) { revert(); }

        Order storage order = orderBook[_orderId];
        Agreement storage agreement = agreements[_orderId][_agreementId];

        // すでに支払い済みの場合、エラーを返す
        if (agreement.paid) { revert(); }
        // 元注文で指定した決済業者とは異なる場合、エラーを返す
        if (msg.sender != order.agent) { revert(); }

        // キャンセル済みフラグをキャンセル（True）に更新する
        agreements[_orderId][_agreementId].canceled = true;

        if (order.isBuy) {
            SettlementNG(order.token, _orderId, _agreementId, order.owner, agreement.counterpart, order.price, agreement.amount, order.agent);
        } else {
            // 売り注文の場合、預かりを解放 -> 預かりの引き出し
            // 取り消した注文は無効化する（注文中状態に戻さない）
            commitments[order.owner][order.token] = commitments[order.owner][order.token].sub(order.amount);
            IbetStraightBond(order.token).transfer(order.owner,order.amount);
            SettlementNG(order.token, _orderId, _agreementId, agreement.counterpart, order.owner, order.price, agreement.amount, order.agent);
        }

        return true;
    }

    // ERC223 token deposit handler
    function tokenFallback(address _from, uint _value, bytes /*_data*/) public{
        balances[_from][msg.sender] = balances[_from][msg.sender].add(_value);
    }

}
