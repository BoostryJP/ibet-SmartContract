pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./IbetStandardTokenInterface.sol";
import "./ExchangeStorageModel.sol";
import "./OTCExchangeStorage.sol";
import "./PaymentGateway.sol";
import "./PersonalInfo.sol";
import "./RegulatorService.sol";


contract IbetOTCExchange is Ownable, ExchangeStorageModel {
    using SafeMath for uint256;

    // 約定明細の有効期限
    //  Note:
    //   現在の設定値は14日で設定している（長期の連休を考慮）。
    uint256 lockingPeriod = 1209600;

    // ---------------------------------------------------------------
    // Event
    // ---------------------------------------------------------------

    // Event: 注文
    event NewOrder(
        address indexed tokenAddress,
        uint256 orderId,
        address indexed ownerAddress,
        address indexed counterpartAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event: 注文取消
    event CancelOrder(
        address indexed tokenAddress,
        uint256 orderId,
        address indexed ownerAddress,
        address indexed counterpartAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event: 約定
    event Agree(
        address indexed tokenAddress,
        uint256 orderId,
        uint256 agreementId,
        address indexed buyAddress,
        address indexed sellAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event: 決済OK
    event SettlementOK(
        address indexed tokenAddress,
        uint256 orderId,
        uint256 agreementId,
        address indexed buyAddress,
        address indexed sellAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event: 決済NG
    event SettlementNG(
        address indexed tokenAddress,
        uint256 orderId,
        uint256 agreementId,
        address indexed buyAddress,
        address indexed sellAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event: 全引き出し
    event Withdrawal(
        address indexed tokenAddress,
        address indexed accountAddress
    );

    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    address public personalInfoAddress;
    address public paymentGatewayAddress;
    address public storageAddress;
    address public regulatorServiceAddress;

    constructor(
        address _paymentGatewayAddress,
        address _personalInfoAddress,
        address _storageAddress,
        address _regulatorServiceAddress

    ) public {
        paymentGatewayAddress = _paymentGatewayAddress;
        personalInfoAddress = _personalInfoAddress;
        storageAddress = _storageAddress;
        regulatorServiceAddress = _regulatorServiceAddress;
    }

    // -------------------------------------------------------------------
    // Function: getter/setter
    // -------------------------------------------------------------------

    function getOrder(uint256 _orderId)
        public
        view
        returns (
        address _owner,
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent,
        bool _canceled
        )
    {
        // 取引関係者限定
        ExchangeStorageModel.OTCOrder memory _order = OTCExchangeStorage(storageAddress).getOrder(_orderId);
        require(_order.owner == msg.sender || _order.counterpart == msg.sender || _order.agent == msg.sender);
        return (
           _order.owner,
           _order.counterpart,
           _order.token,
           _order.amount,
           _order.price,
           _order.agent,
           _order.canceled
        );
    }

    function setOrder(
        uint256 _orderId,
        address _owner,
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent,
        bool _canceled
    ) private returns (bool) {
        ExchangeStorageModel.OTCOrder memory _order = ExchangeStorageModel.mappingOTCOrder(
            _owner,
            _counterpart,
            _token,
            _amount,
            _price,
            _agent,
            _canceled
        );
        OTCExchangeStorage(storageAddress).setOrder(
            _orderId,
            _order
        );
        return true;
    }

    function getAgreement(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns (
            address _counterpart,
            uint256 _amount,
            uint256 _price,
            bool _canceled,
            bool _paid,
            uint256 _expiry
        )
    {
        // 取引関係者限定
        ExchangeStorageModel.OTCOrder memory _order = OTCExchangeStorage(storageAddress).getOrder(_orderId);
        require(_order.owner == msg.sender || _order.counterpart == msg.sender || _order.agent == msg.sender);
        
        ExchangeStorageModel.OTCAgreement memory _agreement = OTCExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);
        return (
           _agreement.counterpart,
           _agreement.amount,
           _agreement.price,
           _agreement.canceled,
           _agreement.paid,
           _agreement.expiry
        );
    }

    function setAgreement(
        uint256 _orderId,
        uint256 _agreementId,
        address _counterpart,
        uint256 _amount,
        uint256 _price,
        bool _canceled,
        bool _paid,
        uint256 _expiry
    ) private returns (bool) {

     ExchangeStorageModel.OTCAgreement memory _agreement = ExchangeStorageModel.mappingOTCAgreement(
        _counterpart,
        _amount,
        _price,
        _canceled,
        _paid,
        _expiry
     );
        OTCExchangeStorage(storageAddress).setAgreement(
            _orderId,
            _agreementId,
            _agreement
        );
        return true;
    }

    // Latest Order ID
    function latestOrderId() public view returns (uint256) {
        return OTCExchangeStorage(storageAddress).getLatestOrderId();
    }

    function setLatestOrderId(uint256 _value) private returns (bool) {
        OTCExchangeStorage(storageAddress).setLatestOrderId(_value);
        return true;
    }

    // Latest Agreement ID
    function latestAgreementId(uint256 _orderId) public view returns (uint256) {
        return
            OTCExchangeStorage(storageAddress).getLatestAgreementId(_orderId);
    }

    function setLatestAgreementId(uint256 _orderId, uint256 _value)
        private
        returns (bool)
    {
        OTCExchangeStorage(storageAddress).setLatestAgreementId(
            _orderId,
            _value
        );
        return true;
    }

    // Balance
    function balanceOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return OTCExchangeStorage(storageAddress).getBalance(_account, _token);
    }

    function setBalance(address _account, address _token, uint256 _value)
        private
        returns (bool)
    {
        return
            OTCExchangeStorage(storageAddress).setBalance(
                _account,
                _token,
                _value
            );
    }

    // Commitment
    function commitmentOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return
            OTCExchangeStorage(storageAddress).getCommitment(_account, _token);
    }

    function setCommitment(address _account, address _token, uint256 _value)
        private
        returns (bool)
    {
        OTCExchangeStorage(storageAddress).setCommitment(
            _account,
            _token,
            _value
        );
        return true;
    }

    // ---------------------------------------------------------------
    // Function: Logic
    // ---------------------------------------------------------------

    // Function: （投資家）新規注文を作成する　Make注文
    function createOrder(
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent
    ) public returns (bool) {
        // <CHK>
        //  取引参加者チェック
        if (regulatorServiceAddress != address(0)) {
            require(RegulatorService(regulatorServiceAddress).check(msg.sender) == 0 || RegulatorService(regulatorServiceAddress).check(_counterpart) == 0);
        }

        // <CHK>
        //  1) 注文数量が0の場合
        //  2) 残高数量が発注数量に満たない場合
        //  3) 認可されたアドレスではない場合
        //  4) 名簿用個人情報が登録されていない場合
        //  5) 取扱ステータスがFalseの場合
        //  6) 有効な収納代行業者（Agent）を指定していない場合
        //   -> 更新処理: 全ての残高を投資家のアカウントに戻し、falseを返す
        if (
            _amount == 0 ||
            balanceOf(msg.sender, _token) < _amount ||
            PaymentGateway(paymentGatewayAddress).accountApproved(msg.sender, _agent) == false ||
            PersonalInfo(personalInfoAddress).isRegistered(msg.sender, IbetStandardTokenInterface(_token).owner()) == false ||
            IbetStandardTokenInterface(_token).status() == false ||
            validateAgent(_agent) == false
        ) {
            IbetStandardTokenInterface(_token).transfer(
                msg.sender,
                balanceOf(msg.sender, _token)
            );
            setBalance(msg.sender, _token, 0);
            return false;
        }

        // 更新処理: 注文IDをカウントアップ -> 注文情報を挿入
        uint256 orderId = latestOrderId() + 1;
        setLatestOrderId(orderId);
        setOrder(
            orderId,
            msg.sender,
            _counterpart,
            _token,
            _amount,
            _price,
            _agent,
            false
        );

        // 預かりを拘束
        setBalance(
            msg.sender,
            _token,
            balanceOf(msg.sender, _token).sub(_amount)
        );
        setCommitment(
            msg.sender,
            _token,
            commitmentOf(msg.sender, _token).add(_amount)
        );

        // イベント登録: 新規注文
        emit NewOrder(
            _token,
            orderId,
            msg.sender,
            _counterpart,
            _price,
            _amount,
            _agent
        );

        return true;
    }

    // Function: （投資家）注文をキャンセルする
    function cancelOrder(uint256 _orderId) public returns (bool) {
        // <CHK>
        //  指定した注文番号が、直近の注文ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());

        ExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        // <CHK>
        //  1) 元注文の残注文数量が0の場合
        //  2) 注文がキャンセル済みの場合
        //  3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
        //   -> REVERT
        if (
            order.amount == 0 ||
            order.canceled == true ||
            order.owner != msg.sender
        ) {
            revert();
        }

        // 注文で拘束している預かりを解放 => 残高を投資家のアカウントに戻す
        setCommitment(
            msg.sender,
            order.token,
            commitmentOf(msg.sender, order.token).sub(order.amount)
        );
        IbetStandardTokenInterface(order.token).transfer(
            msg.sender,
            order.amount
        );

        // 更新処理: キャンセル済みフラグをキャンセル済み（True）に更新
         OTCExchangeStorage(storageAddress).setOrderCanceled(_orderId, true);

        // イベント登録: 注文キャンセル
        emit CancelOrder(
            order.token,
            _orderId,
            msg.sender,
            order.counterpart,
            order.price,
            order.amount,
            order.agent
        );

        return true;
    }

    // Function: （投資家）注文に応じる　Take注文 -> 約定
    // NOTE: 約定数量 = 注文数量
    function executeOrder(uint256 _orderId)
        public
        returns (bool)
    {
        // <CHK>
        //  指定した注文IDが直近の注文IDを超えている場合
        require(_orderId <= latestOrderId());

        ExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        // <CHK>
        //  取引参加者チェック
        if (regulatorServiceAddress != address(0)) {
            require(RegulatorService(regulatorServiceAddress).check(msg.sender) == 0 || RegulatorService(regulatorServiceAddress).check(order.owner) == 0);
        }

        
        // <CHK>
        // 取引関係者限定
        require(order.owner == msg.sender || order.counterpart == msg.sender || order.agent == msg.sender);

        // <CHK>
        //  1) 元注文の発注者と同一のアドレスからの発注の場合
        //  2) 元注文がキャンセル済の場合
        //  3) 認可されたアドレスではない場合
        //  4) 名簿用個人情報が登録されていない場合
        //  5) 買注文者がコントラクトアドレスの場合
        //  6) 取扱ステータスがFalseの場合
        //   -> REVERT
        if (
            msg.sender == order.owner ||
            order.canceled == true ||
            PaymentGateway(paymentGatewayAddress).accountApproved(msg.sender,order.agent) == false ||
            PersonalInfo(personalInfoAddress).isRegistered(msg.sender,IbetStandardTokenInterface(order.token).owner()) == false ||
            isContract(msg.sender) == true ||
            IbetStandardTokenInterface(order.token).status() == false
            )
        {
            revert();
        }

        // 更新処理: 約定IDをカウントアップ => 約定情報を挿入する
        uint256 agreementId = latestAgreementId(_orderId) + 1;
        setLatestAgreementId(_orderId, agreementId);
        uint256 expiry = now + lockingPeriod;
        setAgreement(
            _orderId,
            agreementId,
            msg.sender,
            order.amount,
            order.price,
            false,
            false,
            expiry
        );

        // 更新処理: 元注文の数量を0にする
         OTCExchangeStorage(storageAddress).setOrderAmount(_orderId, 0);
           
         // イベント登録: 約定
        emit Agree(
                order.token,
                _orderId,
                agreementId,
                msg.sender,
                order.owner,
                order.price,
                order.amount,
                order.agent
        );
        return true;
    }

    // Function: （決済業者）決済処理 -> 預かりの移動 -> 預かりの引き出し
    function confirmAgreement(uint256 _orderId, uint256 _agreementId)
        public
        returns (bool)
    {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 指定した約定IDが、直近の約定ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());
        require(_agreementId <= latestAgreementId(_orderId));

        ExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        ExchangeStorageModel.OTCAgreement memory agreement = OTCExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);

        // <CHK>
        //  1) すでに決済承認済み（支払い済み）の場合
        //  2) すでに決済非承認済み（キャンセル済み）の場合
        //  3) 元注文で指定した決済業者ではない場合
        //   -> REVERT
        if (agreement.paid || agreement.canceled || msg.sender != order.agent) {
            revert();
        }

        // 更新処理: 支払い済みフラグを支払い済み（True）に更新する
         OTCExchangeStorage(storageAddress).setAgreementPaid(_orderId, _agreementId, true);

        // 更新処理: 注文者（売り手）から突合相手（買い手）へと資産移転を行う
        setCommitment(
            order.owner,
            order.token,
            commitmentOf(order.owner, order.token).sub(agreement.amount)
        );
        IbetStandardTokenInterface(order.token).transfer(
            agreement.counterpart,
            agreement.amount
        );
        // イベント登録: 決済OK
        emit SettlementOK(
            order.token,
            _orderId,
            _agreementId,
            agreement.counterpart,
            order.owner,
            order.price,
            agreement.amount,
            order.agent
        );

        return true;
    }

    // Function: （決済業者）約定キャンセル
    function cancelAgreement(uint256 _orderId, uint256 _agreementId)
        public
        returns (bool)
    {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 指定した約定IDが、直近の約定ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());
        require(_agreementId <= latestAgreementId(_orderId));

        ExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        ExchangeStorageModel.OTCAgreement memory agreement = OTCExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);

        if (agreement.expiry <= now) {
            // 約定明細の有効期限を超過している場合
            // <CHK>
            //  1) すでに決済承認済み（支払い済み）の場合
            //  2) すでに決済非承認済み（キャンセル済み）の場合
            //  3) msg.senderが、 決済代行（agent）、発注者（owner）、約定相手（counterpart）以外の場合
            //   -> REVERT
            if (
                agreement.paid ||
                agreement.canceled ||
                (msg.sender != order.agent &&
                    msg.sender != order.owner &&
                    msg.sender != agreement.counterpart)
            ) {
                revert();
            }
        } else {
            // 約定明細の有効期限を超過していない場合
            // <CHK>
            //  1) すでに支払い済みの場合
            //  2) すでに決済非承認済み（キャンセル済み）の場合
            //  3) msg.senderが、決済代行（agent）以外の場合
            //   -> REVERT
            if (
                agreement.paid ||
                agreement.canceled ||
                msg.sender != order.agent
            ) {
                revert();
            }
        }

        // 更新処理: キャンセル済みフラグをキャンセル（True）に更新する
         OTCExchangeStorage(storageAddress).setAgreementCanceled( _orderId, _agreementId, true);

        // 更新処理: 突合相手（買い手）の注文数量だけ注文者（売り手）の預かりを解放
        //  -> 預かりの引き出し。
        // 取り消した注文は無効化する（注文中状態に戻さない）
        setCommitment(
            order.owner,
            order.token,
            commitmentOf(order.owner, order.token).sub(agreement.amount)
        );
        IbetStandardTokenInterface(order.token).transfer(
            order.owner,
            agreement.amount
        );
        // イベント登録: 決済NG
        emit SettlementNG(
            order.token,
            _orderId,
            _agreementId,
            agreement.counterpart,
            order.owner,
            order.price,
            agreement.amount,
            order.agent
        );

        return true;
    }

    // Function: （投資家）全ての預かりを引き出しする
    //  Note:
    //   未売却の預かり（balances）に対してのみ引き出しをおこなう。
    //   約定済、注文中の預かり（commitments）の引き出しはおこなわない。
    function withdrawAll(address _token) public returns (bool) {
        uint256 balance = balanceOf(msg.sender, _token);

        // <CHK>
        //  残高がゼロの場合、REVERT
        if (balance == 0) {
            revert();
        }

        // 更新処理: トークン引き出し（送信）
        IbetStandardTokenInterface(_token).transfer(msg.sender, balance);
        setBalance(msg.sender, _token, 0);

        // イベント登録
        emit Withdrawal(_token, msg.sender);

        return true;
    }

    // Function:  Deposit Handler
    function tokenFallback(
        address _from,
        uint256 _value,
        bytes memory /*_data*/
    ) public {
        setBalance(_from, msg.sender, balanceOf(_from, msg.sender).add(_value));
    }

    // ファンクション: アドレスフォーマットがコントラクトのものかを判断する
    function isContract(address _addr) private view returns (bool is_contract) {
        uint256 length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    // ファンクション: 新規注文時に指定したagentアドレスが有効なアドレスであることをチェックする
    function validateAgent(address _addr)
        private
        view
        returns (bool)
    {
        return PaymentGateway(paymentGatewayAddress).getAgent(_addr);
    }
}
