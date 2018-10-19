pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./IbetMembership.sol";

contract IbetMembershipExchange is Ownable {
    using SafeMath for uint256;

    // 約定明細の有効期限
    //  Note:
    //   現在の設定値は14日で設定している（長期の連休を考慮）。
    uint256 lockingPeriod = 1209600;

    // 注文情報
    struct Order {
        address owner;
        address token;
        uint256 amount; // 数量
        uint256 price; // 価格
        bool isBuy; // 売買区分（買い：True）
        address agent; // 決済業者のアドレス
        bool canceled; // キャンセル済みフラグ
    }

    // 約定情報
    struct Agreement {
        address counterpart; // 約定相手
        uint256 amount; // 約定数量
        uint256 price; // 約定価格
        bool canceled; // キャンセル済みフラグ
        bool paid; // 支払い済みフラグ
        uint256 expiry; // 有効期限（約定から１４日）
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
    event NewOrder(address indexed tokenAddress, uint256 orderId,
        address indexed accountAddress, bool indexed isBuy, uint256 price,
        uint256 amount, address agentAddress);

    // イベント：注文取消
    event CancelOrder(address indexed tokenAddress, uint256 orderId,
        address indexed accountAddress, bool indexed isBuy, uint256 price,
        uint256 amount, address agentAddress);

    // イベント：約定
    event Agree(address indexed tokenAddress, uint256 orderId,
        uint256 agreementId, address indexed buyAddress,
        address indexed sellAddress, uint256 price, uint256 amount,
        address agentAddress);

    // イベント：決済OK
    event SettlementOK(address indexed tokenAddress, uint256 orderId,
        uint256 agreementId, address indexed buyAddress,
        address indexed sellAddress, uint256 price, uint256 amount,
        address agentAddress);

    // イベント：決済NG
    event SettlementNG(address indexed tokenAddress, uint256 orderId,
        uint256 agreementId, address indexed buyAddress,
        address indexed sellAddress, uint256 price,
        uint256 amount, address agentAddress);

    // イベント：全引き出し
    event Withdrawal(address indexed tokenAddress, address indexed accountAddress);

    // イベント：送信
    event Transfer(address indexed tokenAddress, address indexed from,
        address indexed to, uint256 value);

    // コンストラクタ
    constructor() public {}

    // ファンクション：（投資家）新規注文を作成する　Make注文
    function createOrder(address _token, uint256 _amount, uint256 _price,
        bool _isBuy, address _agent)
        public
        returns (bool)
    {
        if (_isBuy == true) { // 買注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 取扱ステータスがFalseの場合
            //   -> REVERT
            if (_amount == 0 ||
                IbetMembership(_token).status() == false)
            {
                revert();
            }
        }

        if (_isBuy == false) { // 売注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 残高数量が発注数量に満たない場合
            //  3) 取扱ステータスがFalseの場合
            //   -> 更新処理：全ての残高を投資家のアカウントに戻し、falseを返す
            if (_amount == 0 ||
                balances[msg.sender][_token] < _amount ||
                IbetMembership(_token).status() == false)
            {
                IbetMembership(_token).transfer(msg.sender,balances[msg.sender][_token]);
                balances[msg.sender][_token] = 0;
                return false;
            }
        }

        // 更新処理：注文IDをカウントアップ -> 注文情報を挿入
        uint256 orderId = latestOrderId++;
        orderBook[orderId] = Order(msg.sender, _token, _amount, _price,
                                  _isBuy, _agent, false);

        // 更新処理：売り注文の場合、預かりを拘束
        if (!_isBuy) {
            balances[msg.sender][_token] = balances[msg.sender][_token].sub(_amount);
            commitments[msg.sender][_token] = commitments[msg.sender][_token].add(_amount);
        }

        // イベント登録：新規注文
        emit NewOrder(_token, orderId, msg.sender, _isBuy, _price, _amount, _agent);

        return true;
    }

    // ファンクション：（投資家）注文をキャンセルする
    function cancelOrder(uint256 _orderId) public returns (bool) {
        // <CHK>
        //  指定した注文番号が、直近の注文ID以上の場合
        //   -> REVERT
        require(_orderId < latestOrderId);

        Order storage order = orderBook[_orderId];

        // <CHK>
        //  1) 元注文の残注文数量が0の場合
        //  2) 注文がキャンセル済みの場合
        //  3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
        //   -> REVERT
        if (order.amount == 0 ||
            order.canceled == true ||
            order.owner != msg.sender) {
            revert();
        }

        // 更新処理：売り注文の場合、注文で拘束している預かりを解放 => 残高を投資家のアカウントに戻す
        if (!order.isBuy) {
            commitments[msg.sender][order.token] =
                commitments[msg.sender][order.token].sub(order.amount);
            IbetMembership(order.token).transfer(msg.sender,order.amount);
        }

        // 更新処理：キャンセル済みフラグをキャンセル済み（True）に更新
        order.canceled = true;

        // イベント登録：注文キャンセル
        emit CancelOrder(order.token, _orderId, msg.sender,
                        order.isBuy, order.price, order.amount, order.agent);

        return true;
    }

    // ファンクション：（投資家）注文に応じる　Take注文 -> 約定
    function executeOrder(uint256 _orderId, uint256 _amount, bool _isBuy)
        public
        returns (bool)
    {
        // <CHK>
        //  指定した注文IDが直近の注文IDを超えている場合
        require(_orderId < latestOrderId);

        Order storage order = orderBook[_orderId];
        require(order.owner != 0x0000000000000000000000000000000000000000);

        if (_isBuy == true) { // 買注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 元注文と、発注する注文が同一の売買区分の場合
            //  3) 元注文の発注者と同一のアドレスからの発注の場合
            //  4) 元注文がキャンセル済の場合
            //  5) 取扱ステータスがFalseの場合
            //  6) 数量が元注文の残数量を超過している場合
            //   -> REVERT
            if (_amount == 0 ||
                order.isBuy == _isBuy ||
                msg.sender == order.owner ||
                order.canceled == true ||
                IbetMembership(order.token).status() == false ||
                order.amount < _amount )
            {
                revert();
            }
        }

        if (_isBuy == false) { // 売注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 元注文と、発注する注文が同一の売買区分の場合
            //  3) 元注文の発注者と同一のアドレスからの発注の場合
            //  4) 元注文がキャンセル済の場合
            //  5) 取扱ステータスがFalseの場合
            //  6) 発注者の残高が発注数量を下回っている場合
            //  7) 数量が元注文の残数量を超過している場合
            //   -> 更新処理：残高を投資家のアカウントに全て戻し、falseを返す
            if (_amount == 0 ||
                order.isBuy == _isBuy ||
                msg.sender == order.owner ||
                order.canceled == true ||
                IbetMembership(order.token).status() == false ||
                balances[msg.sender][order.token] < _amount ||
                order.amount < _amount )
            {
                IbetMembership(order.token).transfer(msg.sender,
                    balances[msg.sender][order.token]);
                balances[msg.sender][order.token] = 0;
                return false;
            }
        }

        // 更新処理：約定IDをカウントアップ => 約定情報を挿入する
        uint256 latestAgreementId = latestAgreementIds[_orderId]++;
        uint256 _expiry = now + lockingPeriod;
        agreements[_orderId][latestAgreementId] =
            Agreement(msg.sender, _amount, order.price, false, false, _expiry);

        // 更新処理：元注文の数量を減らす
        order.amount = order.amount.sub(_amount);

        if (order.isBuy) {
            // 更新処理：買い注文に対して売り注文で応じた場合、売りの預かりを拘束
            balances[msg.sender][order.token] =
                balances[msg.sender][order.token].sub(_amount);
            commitments[msg.sender][order.token] =
                commitments[msg.sender][order.token].add(_amount);
            // イベント登録：約定
            emit Agree(order.token, _orderId, latestAgreementId, order.owner,
                msg.sender, order.price, _amount, order.agent);
        } else {
            // イベント登録：約定
            emit Agree(order.token, _orderId, latestAgreementId,
                msg.sender, order.owner, order.price, _amount, order.agent);
        }

        // 更新処理：現在値を更新する
        lastPrice[order.token] = order.price;

        return true;
    }

    // ファンクション：（決済業者）決済処理 -> 預かりの移動 -> 預かりの引き出し
    function confirmAgreement(uint256 _orderId, uint256 _agreementId)
        public
        returns (bool)
    {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 指定した約定IDが、直近の約定ID以上の場合
        //   -> REVERT
        require(_orderId < latestOrderId);
        require(_agreementId < latestAgreementIds[_orderId]);

        Order storage order = orderBook[_orderId];
        Agreement storage agreement = agreements[_orderId][_agreementId];

        // <CHK>
        //  1) すでに決済承認済み（支払い済み）の場合
        //  2) すでに決済非承認済み（キャンセル済み）の場合
        //  3) 元注文で指定した決済業者ではない場合
        //   -> REVERT
        if (agreement.paid ||
            agreement.canceled ||
            msg.sender != order.agent) {
            revert();
        }

        // 更新処理：支払い済みフラグを支払い済み（True）に更新する
        agreement.paid = true;

        if (order.isBuy) {
            // 更新処理：買注文の場合、突合相手（売り手）から注文者（買い手）へと資産移転を行う
            commitments[agreement.counterpart][order.token] =
                commitments[agreement.counterpart][order.token].sub(agreement.amount);
            IbetMembership(order.token).transfer(order.owner,agreement.amount);
            // イベント登録：決済OK
            emit SettlementOK(order.token, _orderId, _agreementId,
                order.owner, agreement.counterpart, order.price,
                agreement.amount, order.agent);
        } else {
            // 更新処理：売注文の場合、注文者（売り手）から突合相手（買い手）へと資産移転を行う
            commitments[order.owner][order.token] =
                commitments[order.owner][order.token].sub(agreement.amount);
            IbetMembership(order.token).transfer(agreement.counterpart,
                                                  agreement.amount);
            // イベント登録：決済OK
            emit SettlementOK(order.token, _orderId, _agreementId,
                agreement.counterpart, order.owner, order.price,
                agreement.amount, order.agent);
        }

        return true;
    }

    // ファンクション：（決済業者）約定キャンセル
    function cancelAgreement(uint256 _orderId, uint256 _agreementId)
        public
        returns (bool)
    {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 指定した約定IDが、直近の約定ID以上の場合
        //   -> REVERT
        require(_orderId < latestOrderId);
        require(_agreementId < latestAgreementIds[_orderId]);

        Order storage order = orderBook[_orderId];
        Agreement storage agreement = agreements[_orderId][_agreementId];

        if (agreement.expiry <= now) { // 約定明細の有効期限を超過している場合
          // <CHK>
          //  1) すでに決済承認済み（支払い済み）の場合
          //  2) すでに決済非承認済み（キャンセル済み）の場合
          //  3) msg.senderが、 決済代行（agent）、発注者（owner）、約定相手（counterpart）以外の場合
          //   -> REVERT
          if (agreement.paid ||
              agreement.canceled ||
              (
                msg.sender != order.agent &&
                msg.sender != order.owner &&
                msg.sender != agreement.counterpart
              )
          ) {
              revert();
          }
        } else { // 約定明細の有効期限を超過していない場合
          // <CHK>
          //  1) すでに支払い済みの場合
          //  2) すでに決済非承認済み（キャンセル済み）の場合
          //  3) msg.senderが、決済代行（agent）以外の場合
          //   -> REVERT
          if (agreement.paid ||
              agreement.canceled ||
              msg.sender != order.agent
          ) {
              revert();
          }
        }

        // 更新処理：キャンセル済みフラグをキャンセル（True）に更新する
        agreements[_orderId][_agreementId].canceled = true;

        if (order.isBuy) {
            // 更新処理：買い注文の場合、突合相手（売り手）の預かりを解放 -> 預かりの引き出し
            // 取り消した注文は無効化する（注文中状態に戻さない）
            commitments[agreement.counterpart][order.token] =
                commitments[agreement.counterpart][order.token].sub(agreement.amount);
            IbetMembership(order.token).transfer(agreement.counterpart,
                                                  agreement.amount);
            // イベント登録：決済NG
            emit SettlementNG(order.token, _orderId, _agreementId,
                order.owner, agreement.counterpart, order.price,
                agreement.amount, order.agent);
        } else {
            // 更新処理：売り注文の場合、突合相手（買い手）の注文数量だけ注文者（売り手）の預かりを解放
            //  -> 預かりの引き出し。
            // 取り消した注文は無効化する（注文中状態に戻さない）
            commitments[order.owner][order.token] =
                commitments[order.owner][order.token].sub(agreement.amount);
            IbetMembership(order.token).transfer(order.owner,agreement.amount);
            // イベント登録：決済NG
            emit SettlementNG(order.token, _orderId, _agreementId,
                agreement.counterpart, order.owner, order.price,
                agreement.amount, order.agent);
        }

        return true;
    }

    // ファンクション：（投資家）全ての預かりを引き出しする
    //  Note:
    //   未売却の預かり（balances）に対してのみ引き出しをおこなう。
    //   約定済、注文中の預かり（commitments）の引き出しはおこなわない。
    function withdrawAll(address _token) public returns (bool) {

        // <CHK>
        //  残高がゼロの場合、REVERT
        if (balances[msg.sender][_token] == 0 ) { revert(); }

        // 更新処理：トークン引き出し（送信）
        IbetMembership(_token).transfer(msg.sender,balances[msg.sender][_token]);
        balances[msg.sender][_token] = 0;

        // イベント登録
        emit Withdrawal(_token, msg.sender);

        return true;
    }

    // ファンクション：トークンを送信する
    function transfer(address _token, address _to, uint256 _value)
        public
        returns (bool)
    {
        // <CHK>
        //  1) 送信数量が0の場合
        //  2) 残高数量が送信数量に満たない場合
        //   -> 更新処理：全ての残高をsenderのアカウントに戻し、falseを返す
        if (_value == 0 ||
            balances[msg.sender][_token] < _value) {
            IbetMembership(_token).transfer(msg.sender,
                                              balances[msg.sender][_token]);
            balances[msg.sender][_token] = 0;
            return false;
        }

        // 更新処理：トークン送信
        balances[msg.sender][_token] = balances[msg.sender][_token].sub(_value);
        IbetMembership(_token).transfer(_to, _value);

        // イベント登録
        emit Transfer(_token, msg.sender, _to, _value);

        return true;
    }

    // ERC223 token deposit handler
    function tokenFallback(address _from, uint _value, bytes /*_data*/) public{
        balances[_from][msg.sender] = balances[_from][msg.sender].add(_value);
    }

}
