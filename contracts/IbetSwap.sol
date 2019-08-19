pragma solidity ^0.4.24;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./IbetStandardTokenInterface.sol";
import "./ExchangeStorage.sol";

/**
 * @title IbetSwap
 * @notice SettlementトークンとIbetStandardTokenInterface準拠トークン（ISToken）の交換所機能を提供
 * @dev ISToken同士の交換は不可
 */
contract IbetSwap is Ownable{
    using SafeMath for uint256;

    // マーケットメイカー
    //  tokenAddress => accountAddress
    mapping (address => address) public marketMaker;

    // ---------------------------------------------------------------
    // Event
    // ---------------------------------------------------------------

    // Event：Make注文
    event MakeOrder(address indexed tokenAddress, address indexed SettlementTokenAddress, address indexed accountAddress,
        uint256 orderId, bool isBuy, uint256 price, uint256 amount);

    // Event：注文取消
    event ChangeOrder(address indexed tokenAddress, address indexed SettlementTokenAddress, address indexed accountAddress,
        uint256 orderId, bool isBuy, uint256 price, uint256 amount);

    // Event：注文取消
    event CancelOrder(address indexed tokenAddress, address indexed SettlementTokenAddress, address indexed accountAddress,
        uint256 orderId, bool isBuy, uint256 price, uint256 amount);

    // Event：約定
    event Agree(address tokenAddress, address SettlementTokenAddress,
        uint256 orderId, uint256 agreementId,
        address indexed buyerAddress, address indexed sellerAddress,
        uint256 price, uint256 amount);

    // Event：全引き出し
    event Withdrawal(address indexed tokenAddress, address indexed accountAddress);


    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    address public storageAddress;
    address public settlementTokenAddress;

    constructor(address _storageAddress, address _settlementTokenAddress)
        public
    {
        storageAddress = _storageAddress;
        settlementTokenAddress =_settlementTokenAddress;
    }


    // ---------------------------------------------------------------
    // Function: Storage
    // ---------------------------------------------------------------
    struct Order {
        address owner;
        address token;
        uint256 amount; // 数量
        uint256 price; // 価格
        bool isBuy; // 売買区分（買い：True）
        address agent; // 決済業者のアドレス
        bool canceled; // キャンセル済みフラグ
    }

    struct Agreement {
        address counterpart; // 約定相手
        uint256 amount; // 約定数量
        uint256 price; // 約定価格
        bool canceled; // キャンセル済みフラグ
        bool paid; // 支払い済みフラグ
        uint256 expiry; // 有効期限（なし：約定後の変更不可）
    }

    // Order
    function getOrder(uint256 _orderId)
        public
        view
        returns (address owner, address token, uint256 amount, uint256 price,
        bool isBuy, address agent, bool canceled)
    {
        return ExchangeStorage(storageAddress).getOrder(_orderId);
    }

    function setOrder(
        uint256 _orderId, address _owner, address _token,
        uint256 _amount, uint256 _price, bool _isBuy,
        address _agent, bool _canceled)
        private
        returns (bool)
    {
        ExchangeStorage(storageAddress).setOrder(
            _orderId, _owner, _token, _amount, _price, _isBuy, _agent, _canceled);
        return true;
    }

    // Agreement
    function getAgreement(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns (address _counterpart, uint256 _amount, uint256 _price,
        bool _canceled, bool _paid, uint256 _expiry)
    {
        return ExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);
    }

    function setAgreement(uint256 _orderId, uint256 _agreementId,
        address _counterpart, uint256 _amount, uint256 _price,
        bool _canceled, bool _paid, uint256 _expiry)
        private
        returns (bool)
    {
        ExchangeStorage(storageAddress).setAgreement(
            _orderId, _agreementId, _counterpart, _amount, _price, _canceled, _paid, _expiry);
        return true;
    }

    // Latest Order ID
    function latestOrderId()
        public
        view
        returns (uint256)
    {
        return ExchangeStorage(storageAddress).getLatestOrderId();
    }

    function setLatestOrderId(uint256 _value)
        private
        returns (bool)
    {
        ExchangeStorage(storageAddress).setLatestOrderId(_value);
        return true;
    }

    // Latest Agreement ID
    function latestAgreementId(uint256 _orderId)
        public
        view
        returns (uint256)
    {
        return ExchangeStorage(storageAddress).getLatestAgreementId(_orderId);
    }

    function setLatestAgreementId(uint256 _orderId, uint256 _value)
        private
        returns (bool)
    {
        ExchangeStorage(storageAddress).setLatestAgreementId(_orderId, _value);
        return true;
    }

    // Balance
    function balanceOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return ExchangeStorage(storageAddress).getBalance(_account, _token);
    }

    function setBalance(address _account, address _token, uint256 _value)
        private
        returns (bool)
    {
        return ExchangeStorage(storageAddress).setBalance(_account, _token, _value);
    }

    // Commitment
    function commitmentOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return ExchangeStorage(storageAddress).getCommitment(_account, _token);
    }

    function setCommitment(address _account, address _token, uint256 _value)
        private
        returns (bool)
    {
        ExchangeStorage(storageAddress).setCommitment(_account, _token, _value);
        return true;
    }


    // ---------------------------------------------------------------
    // Function: Logic
    // ---------------------------------------------------------------

    /**
     * @notice デポジットハンドラ
     * @notice トークンのデポジットによって残高を追加する。
     */
    function tokenFallback(address _from, uint _value, bytes memory /*_data*/)
        public
    {
        setBalance(_from, msg.sender, balanceOf(_from, msg.sender).add(_value));
    }

    /**
     * @notice マーケットメイカー更新
     * @notice マーケットメイカーの更新を行う。
     * @dev Ownerのみ実行が可能。
     */
    function setMarketMaker(address _tokenAddress, address _accountAddress)
        public
        onlyOwner()
    {
        marketMaker[_tokenAddress] = _accountAddress;
    }

    /**
     * @notice マーケットメイカー権限チェック
     * @notice マーケットメイカーの権限を有していることをチェック。
     */
    modifier onlyMarketMaker(address _tokenAddress)
    {
        require(msg.sender == marketMaker[_tokenAddress]);
        _;
    }

    /**
     * @notice Settlementトークン更新
     * @notice Settlementトークンのアドレス情報を更新する。
     * @dev Ownerのみ実行が可能。
     */
    function setSettlementToken(address _settlementTokenAddress)
        public
        onlyOwner()
    {
        settlementTokenAddress = _settlementTokenAddress;
    }

    /**
     * @notice Settlementトークン利用可否チェック
     * @notice Settlementトークンが利用可能なステータスであることをチェックする。
     */
    modifier isSettlementTokenEnabled()
    {
        require(IbetStandardTokenInterface(settlementTokenAddress).status() == true);
        _;
    }

    /**
     * @notice トークン利用可否チェック
     * @notice ISTokenトークンが利用可能なステータスであることをチェックする。
     */
    modifier isTokenEnabled(address _token)
    {
        require(IbetStandardTokenInterface(_token).status() == true);
        _;
    }

    /**
     * @notice 新規注文作成（Make注文）
     * @notice 流動性供給のための注文を作成する。
     * @dev MarketMakerのみ実行が可能。
     * @dev _isBuy == true : ISTokenの買い（SettlementTokenの売り）
     * @dev _isBuy == false : ISTokenの売り（SettlementTokenの買い）
     * @param _token ISTokenのアドレス
     * @param _amount 注文数量
     * @param _price 単価（SettlementTokenの数量）
     * @param _isBuy 売/買（true:買）
     */
    function makeOrder(address _token, uint256 _amount, uint256 _price, bool _isBuy)
        public
        onlyEOA(msg.sender)
        onlyMarketMaker(_token)
        isTokenEnabled(_token)
        isSettlementTokenEnabled()
        returns (bool)
    {
        if (_isBuy) { // 買注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) SettlementToken残高が不足している場合
            //  -> REVERT
            if (_amount == 0 ||
                balanceOf(msg.sender, settlementTokenAddress) < _amount.mul(_price))
            {
                revert();
            }
        }

        if (!_isBuy) { // 売注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) ISToken残高が発注数量に満たない場合
            //  -> REVERT
            if (_amount == 0 ||
                balanceOf(msg.sender, _token) < _amount)
            {
                revert();
            }
        }

        // 更新処理：注文情報
        setLatestOrderId(latestOrderId() + 1);
        setOrder(latestOrderId(), msg.sender, _token, _amount, _price, _isBuy, address(0), false);

        // 更新処理：残高、拘束数量
        if (_isBuy) { // 買注文の場合
            // SettlementToken残高、拘束数量の更新
            setBalance(
                msg.sender,
                settlementTokenAddress,
                balanceOf(msg.sender, settlementTokenAddress).sub(_amount.mul(_price))
            );
            setCommitment(
                msg.sender,
                settlementTokenAddress,
                commitmentOf(msg.sender, settlementTokenAddress).add(_amount.mul(_price))
            );
        } else { // 売注文の場合
            // ISToken残高、拘束数量の更新
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
        }

        // イベント登録：Make注文
        emit MakeOrder(_token, settlementTokenAddress, msg.sender, latestOrderId(),
            _isBuy, _price, _amount);

        return true;
    }

    /**
     * @notice 注文訂正
     * @notice Make注文の訂正を行う。
     * @dev MarketMakerのみ実行が可能。
     * @dev 訂正可能な項目は、注文数量（amount）と単価（price）
     * @param _orderId 注文ID
     * @param _amount 注文数量（訂正後の数量）
     * @param _price 単価（SettlementTokenの数量、訂正後の単価）
     */
    function changeOrder(uint256 _orderId, uint256 _amount, uint256 _price)
        public
        onlyEOA(msg.sender)
        isSettlementTokenEnabled()
        returns (bool)
    {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 数量（amount）がゼロの場合
        //  -> REVERT
        require(_orderId <= latestOrderId());
        if (_amount == 0) revert();

        // 注文情報参照
        Order memory order;
        (order.owner, order.token, order.amount, order.price, order.isBuy, order.agent, order.canceled) =
            getOrder(_orderId);

        // <CHK>
        //  1) 注文がキャンセル済みの場合
        //  2) 元注文の発注者と、注文キャンセルの実施者が異なる場合
        //  -> REVERT
        if (order.canceled == true ||
            order.owner != msg.sender)
        {
            revert();
        }

        // Make買注文に対するCHK処理
        if (order.isBuy) {
            // <CHK>
            //  SettlementToken残高が不足している場合
            //  -> REVERT
            if (balanceOf(msg.sender, settlementTokenAddress).add((order.amount).mul(order.price)) <
                _amount.mul(_price))
            {
                revert();
            }
        }

        // Make売注文に対するCHK処理
        if (!order.isBuy) {
            // <CHK>
            //  ISToken残高が不足している場合
            //  -> REVERT
            if (balanceOf(msg.sender, order.token).add(order.amount) < _amount)
            {
                revert();
            }
        }

        // 更新処理：残高、拘束数量
        if (order.isBuy) { // 買注文の場合
            // SettlementToken残高、拘束数量の更新
            if ((order.amount).mul(order.price) < _amount.mul(_price)) { // 注文総額が増額の場合
                setBalance(
                    msg.sender, settlementTokenAddress,
                    balanceOf(msg.sender, settlementTokenAddress).
                        sub((_amount.mul(_price)).sub((order.amount).mul(order.price)))
                );
                setCommitment(
                    msg.sender, settlementTokenAddress,
                    commitmentOf(msg.sender, settlementTokenAddress).
                        add((_amount.mul(_price)).sub((order.amount).mul(order.price)))
                );
            } else { // 注文総額が減額の場合
                setBalance(
                    msg.sender, settlementTokenAddress,
                    balanceOf(msg.sender, settlementTokenAddress).
                        add(((order.amount).mul(order.price)).sub(_amount.mul(_price)))
                );
                setCommitment(
                    msg.sender, settlementTokenAddress,
                    commitmentOf(msg.sender, settlementTokenAddress).
                        sub(((order.amount).mul(order.price)).sub(_amount.mul(_price)))
                );
            }
        } else { // 売注文の場合
            // ISToken残高、拘束数量の更新
            if (order.amount < _amount) { // 注文数量が増加している場合
                setBalance(
                    msg.sender, order.token,
                    balanceOf(msg.sender, order.token).sub(_amount.sub(order.amount))
                );
                setCommitment(
                    msg.sender, order.token,
                    commitmentOf(msg.sender, order.token).add(_amount.sub(order.amount))
                );
            } else { // 注文数量が減少している場合
                setBalance(
                    msg.sender, order.token,
                    balanceOf(msg.sender, order.token).add((order.amount).sub(_amount))
                );
                setCommitment(
                    msg.sender, order.token,
                    commitmentOf(msg.sender, order.token).sub((order.amount).sub(_amount))
                );
            }
        }

        // 更新処理：注文状態を更新
        setOrder(_orderId, order.owner, order.token,
            _amount, _price, order.isBuy, order.agent, order.canceled
        );

        // イベント登録：注文キャンセル
        emit ChangeOrder(order.token, settlementTokenAddress, msg.sender,
            _orderId, order.isBuy, order.price, order.amount);

        return true;
    }

    /**
     * @notice 注文キャンセル
     * @notice Make注文のキャンセルを行う。
     * @dev MarketMakerのみ実行が可能。
     * @param _orderId 注文ID
     */
    function cancelOrder(uint256 _orderId)
        public
        onlyEOA(msg.sender)
        isSettlementTokenEnabled()
        returns (bool)
    {
        // <CHK>
        //  指定した注文番号が、直近の注文ID以上の場合
        //  -> REVERT
        require(_orderId <= latestOrderId());

        Order memory order;
        (order.owner, order.token, order.amount, order.price, order.isBuy, order.agent, order.canceled) =
            getOrder(_orderId);

        // <CHK>
        //  1) 注文がキャンセル済みの場合
        //  2) 元注文の発注者と、注文キャンセルの実施者が異なる場合
        //  -> REVERT
        if (order.canceled == true ||
            order.owner != msg.sender)
        {
            revert();
        }

        // 更新処理：残高、拘束数量
        if (order.isBuy) { // 買注文の場合
            // SettlementToken残高、拘束数量の更新
            setBalance(
                msg.sender,
                settlementTokenAddress,
                balanceOf(msg.sender, settlementTokenAddress).add(order.amount.mul(order.price))
            );
            setCommitment(
                msg.sender,
                settlementTokenAddress,
                commitmentOf(msg.sender, settlementTokenAddress).sub(order.amount.mul(order.price))
            );
        } else { // 売注文の場合
            // ISToken残高、拘束数量の更新
            setBalance(
                msg.sender,
                order.token,
                balanceOf(msg.sender, order.token).add(order.amount)
            );
            setCommitment(
                msg.sender,
                order.token,
                commitmentOf(msg.sender, order.token).sub(order.amount)
            );
        }

        // 更新処理：注文状態をキャンセル済みに更新
        setOrder(
            _orderId, order.owner, order.token,
            order.amount, order.price, order.isBuy,
            order.agent,
            true
        );

        // イベント登録：注文キャンセル
        emit CancelOrder(order.token, settlementTokenAddress, msg.sender, _orderId, order.isBuy, order.price, order.amount);

        return true;
    }

    /**
     * @notice Take注文
     * @notice 一般ユーザから反対注文（Take注文）を実行する。
     * @dev _isBuy == true : ISTokenの買い（SettlementTokenの売り）
     * @dev _isBuy == false : ISTokenの売り（SettlementTokenの買い）
     * @dev 業務チェックエラー時は、SWAPコントラクトにデポジットしたユーザの預かりを即時でトークンコントラクトに戻す。
     * @param _orderId 注文ID
     * @param _amount 注文数量（ISTokenの数量）
     * @param _isBuy 売/買（true:買）
     */
    function takeOrder(uint256 _orderId, uint256 _amount, bool _isBuy)
        public
        onlyEOA(msg.sender)
        isSettlementTokenEnabled()
        returns (bool)
    {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  -> REVERT
        require(_orderId <= latestOrderId());

        Order memory order;
        (order.owner, order.token, order.amount, order.price, order.isBuy, order.agent, order.canceled) =
            getOrder(_orderId);

        if (_isBuy) { // Take買注文の場合（Make注文は売）
            // <CHK>
            //  1) Take注文数量が0の場合
            //  2) Make注文とTake注文が同一の売買区分の場合
            //  3) Make注文のTake注文の発注者が同一の場合
            //  4) Make注文がキャンセル済の場合
            //  5) トークンの取扱状態が無効（False）の場合
            //  6) Take注文数量がMake注文数量を超えている場合
            //  7) 約定価格（SettlementToken数量）がユーザのSettlementToken残高を超過している場合
            //  -> 更新処理：SettlementToken残高をユーザのアカウントに全て戻し、falseを返す
            if (_amount == 0 ||
                order.isBuy == _isBuy ||
                msg.sender == order.owner ||
                order.canceled == true ||
                IbetStandardTokenInterface(order.token).status() == false ||
                order.amount < _amount ||
                balanceOf(msg.sender, settlementTokenAddress) < _amount.mul(order.price))
            {
                IbetStandardTokenInterface(settlementTokenAddress).transfer(msg.sender, balanceOf(msg.sender, settlementTokenAddress));
                setBalance(msg.sender, settlementTokenAddress, 0);
                return false;
            }
        }

        if (!_isBuy) { // Take売注文の場合（Make注文は買）
            // <CHK>
            //  1) Take注文数量が0の場合
            //  2) Make注文とTake注文が同一の売買区分の場合
            //  3) Make注文のTake注文の発注者が同一の場合
            //  4) Make注文がキャンセル済の場合
            //  5) トークンの取扱状態が無効（False）の場合
            //  6) Take注文数量がMake注文数量を超えている場合
            //  7) Take売注文数量がトークン残高を超過している場合
            //  -> 更新処理：トークン残高をユーザのアカウントに全て戻し、falseを返す
            if (_amount == 0 ||
                order.isBuy == _isBuy ||
                msg.sender == order.owner ||
                order.canceled == true ||
                IbetStandardTokenInterface(order.token).status() == false ||
                order.amount < _amount ||
                balanceOf(msg.sender, order.token) < _amount)
            {
                IbetStandardTokenInterface(order.token).transfer(msg.sender, balanceOf(msg.sender, order.token));
                setBalance(msg.sender, order.token, 0);
                return false;
            }
        }

        // 更新処理：約定情報
        setLatestAgreementId(_orderId, latestAgreementId(_orderId) + 1);
        setAgreement(_orderId, latestAgreementId(_orderId), msg.sender, _amount, order.price, false, true, 0);

        // 更新処理：Make注文の数量を減らす
        setOrder(_orderId, order.owner, order.token, order.amount.sub(_amount),
            order.price, order.isBuy, order.agent, order.canceled);

        if (_isBuy) { // Take買注文の場合（Make注文は売）
            // Makerデータ更新
            //  1) ISToken拘束数量の更新(-)
            //  2) SettlementToken残高の更新(+)
            setCommitment(
                marketMaker[order.token],
                order.token,
                commitmentOf(marketMaker[order.token], order.token).sub(_amount)
            );
            setBalance(
                marketMaker[order.token],
                settlementTokenAddress,
                balanceOf(marketMaker[order.token], settlementTokenAddress).add(_amount.mul(order.price))
            );

            // Takerデータ更新
            //  1) SettlementToken残高の更新(-)
            //  2) ISTokenの割当(+)
            setBalance(
                msg.sender,
                settlementTokenAddress,
                balanceOf(msg.sender, settlementTokenAddress).sub(_amount.mul(order.price))
            );
            IbetStandardTokenInterface(order.token).transfer(msg.sender, _amount);

            // イベント登録：約定
            emit Agree(order.token, settlementTokenAddress, _orderId, latestAgreementId(_orderId),
                msg.sender, order.owner, order.price, _amount);

        } else { // Take売注文の場合（Make注文は買）
            // Makerデータ更新
            //  1) ISToken拘束数量の更新(+)
            //  2) SettlementToken残高の更新(-)
            setCommitment(
                marketMaker[order.token],
                order.token,
                commitmentOf(marketMaker[order.token], order.token).add(_amount)
            );
            setBalance(
                marketMaker[order.token],
                settlementTokenAddress,
                balanceOf(marketMaker[order.token], settlementTokenAddress).sub(_amount.mul(order.price))
            );

            // Takerデータ更新
            //  1) ISToken残高数量の更新(-)
            //  2) SettlementTokenの割当(+)
            setBalance(
                msg.sender,
                order.token,
                balanceOf(msg.sender, order.token).sub(_amount)
            );
            IbetStandardTokenInterface(settlementTokenAddress).transfer(msg.sender, _amount.mul(order.price));

            // イベント登録：約定
            emit Agree(order.token, settlementTokenAddress, _orderId, latestAgreementId(_orderId),
                order.owner, msg.sender, order.price, _amount);
        }

        return true;
    }

    /**
     * @notice 全残高の引き出し
     * @dev 未注文の預かりに対してのみ引き出しをおこなう。
     * @param _token トークンアドレス
     */
    function withdrawAll(address _token)
        public
        onlyEOA(msg.sender)
        onlyMarketMaker(_token)
        returns (bool)
    {
        uint256 balance = balanceOf(msg.sender, _token);

        // <CHK>
        //  残高がゼロの場合、REVERT
        if (balance == 0 ) { revert(); }

        // 更新処理：トークン引き出し（送信）
        IbetStandardTokenInterface(_token).transfer(msg.sender, balance);
        setBalance(msg.sender, _token, 0);

        emit Withdrawal(_token, msg.sender);

        return true;
    }

    /**
     * @notice アドレスフォーマットチェック
     * @notice アドレスフォーマットがコントラクトのものかを判断する。
     */
    function isContract(address _address)
      private
      view
      returns (bool)
    {
      uint length;
      assembly {
        length := extcodesize(_address)
      }
      return (length>0);
    }

    /**
     * @notice EOAアドレスチェック
     * @notice コントラクトアドレスからの実行を不可とする。
     */
    modifier onlyEOA(address _address)
    {
        if (isContract(_address)) revert();
        _;
    }

}
