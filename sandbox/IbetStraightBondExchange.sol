/**
 * Copyright BOOSTRY Co., Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 *
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

pragma solidity ^0.8.23;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./IbetStraightBond.sol";
import "./ExchangeStorage.sol";
import "./PaymentGateway.sol";
import "./PersonalInfo.sol";
import "../interfaces/RegulatorService.sol";
import "../interfaces/ContractReceiver.sol";

/// @title ibet Straight Bond DEX
contract IbetStraightBondExchange is Ownable, ContractReceiver {
    using SafeMath for uint256;

    // 約定明細の有効期限
    // 現在の設定値は14日で設定している（長期の連休を考慮）
    uint256 lockingPeriod = 1209600;

    // ---------------------------------------------------------------
    // Event
    // ---------------------------------------------------------------

    // Event：注文
    event NewOrder(
        address indexed tokenAddress,
        uint256 orderId,
        address indexed accountAddress,
        bool indexed isBuy,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event：注文取消
    event CancelOrder(
        address indexed tokenAddress,
        uint256 orderId,
        address indexed accountAddress,
        bool indexed isBuy,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    // Event：約定
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

    // Event：決済承認
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

    // Event：決済非承認
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

    // Event：全引き出し
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

    // [CONSTRUCTOR]
    /// @param _paymentGatewayAddress PaymentGatewayコントラクトアドレス
    /// @param _personalInfoAddress PersonalInfoコントラクトアドレス
    /// @param _storageAddress ExchangeStorageコントラクトアドレス
    /// @param _regulatorServiceAddress RegulatorServiceコントラクトアドレス
    constructor(
        address _paymentGatewayAddress,
        address _personalInfoAddress,
        address _storageAddress,
        address _regulatorServiceAddress
    ) {
        paymentGatewayAddress = _paymentGatewayAddress;
        personalInfoAddress = _personalInfoAddress;
        storageAddress = _storageAddress;
        regulatorServiceAddress = _regulatorServiceAddress;
    }

    // ---------------------------------------------------------------
    // Function: Storage
    // ---------------------------------------------------------------

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

    /// @notice 注文情報取得
    /// @param _orderId 注文ID
    /// @return owner 注文実行者
    /// @return token トークンアドレス
    /// @return amount 注文数量
    /// @return price 注文単価
    /// @return isBuy 売買区分
    /// @return agent 決済業者のアドレス
    /// @return canceled キャンセル済み状態
    function getOrder(
        uint256 _orderId
    )
        public
        view
        returns (
            address owner,
            address token,
            uint256 amount,
            uint256 price,
            bool isBuy,
            address agent,
            bool canceled
        )
    {
        return ExchangeStorage(storageAddress).getOrder(_orderId);
    }

    /// @notice 注文情報更新
    /// @param _orderId 注文ID
    /// @param _owner 注文実行者
    /// @param _token トークンアドレス
    /// @param _amount 注文数量
    /// @param _price 注文単価
    /// @param _isBuy 売買区分
    /// @param _agent 決済業者のアドレス
    /// @param _canceled キャンセル済み状態
    /// @return 処理結果
    function setOrder(
        uint256 _orderId,
        address _owner,
        address _token,
        uint256 _amount,
        uint256 _price,
        bool _isBuy,
        address _agent,
        bool _canceled
    ) private returns (bool) {
        ExchangeStorage(storageAddress).setOrder(
            _orderId,
            _owner,
            _token,
            _amount,
            _price,
            _isBuy,
            _agent,
            _canceled
        );
        return true;
    }

    /// @notice 約定情報取得
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return _counterpart 約定相手
    /// @return _amount 約定数量
    /// @return _price 約定単価
    /// @return _canceled キャンセル済み状態
    /// @return _paid 支払済状態
    /// @return _expiry 有効期限
    function getAgreement(
        uint256 _orderId,
        uint256 _agreementId
    )
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
        return
            ExchangeStorage(storageAddress).getAgreement(
                _orderId,
                _agreementId
            );
    }

    /// @notice 約定情報更新
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _counterpart 約定相手
    /// @param _amount 約定数量
    /// @param _price 約定単価
    /// @param _canceled キャンセル済み状態
    /// @param _paid 支払済状態
    /// @param _expiry 有効期限
    /// @return 処理結果
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
        ExchangeStorage(storageAddress).setAgreement(
            _orderId,
            _agreementId,
            _counterpart,
            _amount,
            _price,
            _canceled,
            _paid,
            _expiry
        );
        return true;
    }

    /// @notice 直近注文ID取得
    /// @return 直近注文ID
    function latestOrderId() public view returns (uint256) {
        return ExchangeStorage(storageAddress).getLatestOrderId();
    }

    /// @notice 直近注文ID更新
    /// @param _value 更新後の直近注文ID
    /// @return 処理結果
    function setLatestOrderId(uint256 _value) private returns (bool) {
        ExchangeStorage(storageAddress).setLatestOrderId(_value);
        return true;
    }

    /// @notice 直近約定ID取得
    /// @param _orderId 注文ID
    /// @return 直近約定ID
    function latestAgreementId(uint256 _orderId) public view returns (uint256) {
        return ExchangeStorage(storageAddress).getLatestAgreementId(_orderId);
    }

    /// @notice 直近約定ID更新
    /// @param _orderId 注文ID
    /// @param _value 更新後の直近約定ID
    /// @return 処理結果
    function setLatestAgreementId(
        uint256 _orderId,
        uint256 _value
    ) private returns (bool) {
        ExchangeStorage(storageAddress).setLatestAgreementId(_orderId, _value);
        return true;
    }

    /// @notice 残高参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(
        address _account,
        address _token
    ) public view returns (uint256) {
        return ExchangeStorage(storageAddress).getBalance(_account, _token);
    }

    /// @notice 残高数量更新
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の残高数量
    /// @return 処理結果
    function setBalance(
        address _account,
        address _token,
        uint256 _value
    ) private returns (bool) {
        return
            ExchangeStorage(storageAddress).setBalance(
                _account,
                _token,
                _value
            );
    }

    /// @notice 拘束数量参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 拘束数量
    function commitmentOf(
        address _account,
        address _token
    ) public view returns (uint256) {
        return ExchangeStorage(storageAddress).getCommitment(_account, _token);
    }

    /// @notice 拘束数量更新
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の拘束数量
    /// @return 処理結果
    function setCommitment(
        address _account,
        address _token,
        uint256 _value
    ) private returns (bool) {
        ExchangeStorage(storageAddress).setCommitment(_account, _token, _value);
        return true;
    }

    /// @notice 現在値参照
    /// @param _token トークンアドレス
    /// @return 現在値
    function lastPrice(address _token) public view returns (uint256) {
        return ExchangeStorage(storageAddress).getLastPrice(_token);
    }

    /// @notice 現在値更新
    /// @param _token トークンアドレス
    /// @param _value 更新後の現在値
    /// @return 処理結果
    function setLastPrice(
        address _token,
        uint256 _value
    ) private returns (bool) {
        ExchangeStorage(storageAddress).setLastPrice(_token, _value);
        return true;
    }

    // ---------------------------------------------------------------
    // Function: Logic
    // ---------------------------------------------------------------

    /// @notice Make注文
    /// @param _token トークンアドレス
    /// @param _amount 注文数量
    /// @param _price 注文単価
    /// @param _isBuy 売買区分
    /// @param _agent 収納代行業者のアドレス
    /// @return 処理結果
    function createOrder(
        address _token,
        uint256 _amount,
        uint256 _price,
        bool _isBuy,
        address _agent
    ) public returns (bool) {
        // <CHK>
        //  取引参加者チェック
        if (RegulatorService(regulatorServiceAddress).check(msg.sender) != 0)
            revert();

        if (_isBuy == true) {
            // 買注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 認可されたアドレスではない場合
            //  3) 名簿用個人情報が登録されていない場合
            //  4) 買注文者がコントラクトアドレスの場合
            //  5) 償還済みフラグがTrueの場合
            //  6) 取扱ステータスがFalseの場合
            //  7) 有効な収納代行業者（Agent）を指定していない場合
            //   -> REVERT
            if (
                _amount == 0 ||
                PaymentGateway(paymentGatewayAddress).accountApproved(
                    msg.sender,
                    _agent
                ) ==
                    false ||
                PersonalInfo(personalInfoAddress).isRegistered(
                    msg.sender,
                    IbetStraightBond(_token).owner()
                ) ==
                    false ||
                isContract(msg.sender) == true ||
                IbetStraightBond(_token).isRedeemed() == true ||
                IbetStraightBond(_token).status() == false ||
                validateAgent(_agent) == false
            ) {
                revert();
            }
        }

        if (_isBuy == false) {
            // 売注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 残高数量が発注数量に満たない場合
            //  3) 認可されたアドレスではない場合
            //  4) 名簿用個人情報が登録されていない場合
            //  5) 償還済みフラグがTrueの場合
            //  6) 取扱ステータスがFalseの場合
            //  7) 有効な収納代行業者（Agent）を指定していない場合
            //   -> 更新処理：全ての残高を投資家のアカウントに戻し、falseを返す
            if (
                _amount == 0 ||
                balanceOf(msg.sender, _token) < _amount ||
                PaymentGateway(paymentGatewayAddress).accountApproved(
                    msg.sender,
                    _agent
                ) ==
                    false ||
                PersonalInfo(personalInfoAddress).isRegistered(
                    msg.sender,
                    IbetStraightBond(_token).owner()
                ) ==
                    false ||
                IbetStraightBond(_token).isRedeemed() == true ||
                IbetStraightBond(_token).status() == false ||
                validateAgent(_agent) == false
            ) {
                IbetStraightBond(_token).transfer(
                    msg.sender,
                    balanceOf(msg.sender, _token)
                );
                setBalance(msg.sender, _token, 0);
                return false;
            }
        }

        // 更新処理：注文IDをカウントアップ -> 注文情報を挿入
        uint256 orderId = latestOrderId() + 1;
        setLatestOrderId(orderId);
        setOrder(
            orderId,
            msg.sender,
            _token,
            _amount,
            _price,
            _isBuy,
            _agent,
            false
        );

        // 更新処理：売り注文の場合、預かりを拘束
        if (!_isBuy) {
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

        // イベント登録：新規注文
        emit NewOrder(
            _token,
            orderId,
            msg.sender,
            _isBuy,
            _price,
            _amount,
            _agent
        );

        return true;
    }

    /// @notice 注文キャンセル
    /// @param _orderId 注文ID
    /// @return 処理結果
    function cancelOrder(uint256 _orderId) public returns (bool) {
        // <CHK>
        //  指定した注文番号が、直近の注文ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());

        Order memory order;
        (
            order.owner,
            order.token,
            order.amount,
            order.price,
            order.isBuy,
            order.agent,
            order.canceled
        ) = getOrder(_orderId);

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

        // 更新処理：売り注文の場合、注文で拘束している預かりを解放 => 残高を投資家のアカウントに戻す
        if (!order.isBuy) {
            setCommitment(
                msg.sender,
                order.token,
                commitmentOf(msg.sender, order.token).sub(order.amount)
            );
            IbetStraightBond(order.token).transfer(msg.sender, order.amount);
        }

        // 更新処理：キャンセル済みフラグをキャンセル済み（True）に更新
        setOrder(
            _orderId,
            order.owner,
            order.token,
            order.amount,
            order.price,
            order.isBuy,
            order.agent,
            true
        );

        // イベント登録：注文キャンセル
        emit CancelOrder(
            order.token,
            _orderId,
            msg.sender,
            order.isBuy,
            order.price,
            order.amount,
            order.agent
        );

        return true;
    }

    /// @notice Take注文
    /// @param _orderId 注文ID
    /// @param _amount 注文数量
    /// @param _isBuy 売買区分
    /// @return 処理結果
    function executeOrder(
        uint256 _orderId,
        uint256 _amount,
        bool _isBuy
    ) public returns (bool) {
        // <CHK>
        //  取引参加者チェック
        if (RegulatorService(regulatorServiceAddress).check(msg.sender) != 0)
            revert();

        // <CHK>
        //  指定した注文IDが直近の注文IDを超えている場合
        require(_orderId <= latestOrderId());

        Order memory order;
        (
            order.owner,
            order.token,
            order.amount,
            order.price,
            order.isBuy,
            order.agent,
            order.canceled
        ) = getOrder(_orderId);

        require(order.owner != address(0));

        if (_isBuy == true) {
            // 買注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 元注文と、発注する注文が同一の売買区分の場合
            //  3) 元注文の発注者と同一のアドレスからの発注の場合
            //  4) 元注文がキャンセル済の場合
            //  5) 認可されたアドレスではない場合
            //  6) 名簿用個人情報が登録されていない場合
            //  7) 買注文者がコントラクトアドレスの場合
            //  8) 償還済みフラグがTrueの場合
            //  9) 取扱ステータスがFalseの場合
            //  10) 数量が元注文の残数量を超過している場合
            //   -> REVERT
            if (
                _amount == 0 ||
                order.isBuy == _isBuy ||
                msg.sender == order.owner ||
                order.canceled == true ||
                PaymentGateway(paymentGatewayAddress).accountApproved(
                    msg.sender,
                    order.agent
                ) ==
                    false ||
                PersonalInfo(personalInfoAddress).isRegistered(
                    msg.sender,
                    IbetStraightBond(order.token).owner()
                ) ==
                    false ||
                isContract(msg.sender) == true ||
                IbetStraightBond(order.token).isRedeemed() == true ||
                IbetStraightBond(order.token).status() == false ||
                order.amount < _amount
            ) {
                revert();
            }
        }

        if (_isBuy == false) {
            // 売注文の場合
            // <CHK>
            //  1) 注文数量が0の場合
            //  2) 元注文と、発注する注文が同一の売買区分の場合
            //  3) 元注文の発注者と同一のアドレスからの発注の場合
            //  4) 元注文がキャンセル済の場合
            //  5) 認可されたアドレスではない場合
            //  6) 名簿用個人情報が登録されていない場合
            //  7) 償還済みフラグがTrueの場合
            //  8) 取扱ステータスがFalseの場合
            //  9) 発注者の残高が発注数量を下回っている場合
            //  10) 数量が元注文の残数量を超過している場合
            //   -> 更新処理：残高を投資家のアカウントに全て戻し、falseを返す
            if (
                _amount == 0 ||
                order.isBuy == _isBuy ||
                msg.sender == order.owner ||
                order.canceled == true ||
                PaymentGateway(paymentGatewayAddress).accountApproved(
                    msg.sender,
                    order.agent
                ) ==
                    false ||
                PersonalInfo(personalInfoAddress).isRegistered(
                    msg.sender,
                    IbetStraightBond(order.token).owner()
                ) ==
                    false ||
                IbetStraightBond(order.token).isRedeemed() == true ||
                IbetStraightBond(order.token).status() == false ||
                balanceOf(msg.sender, order.token) < _amount ||
                order.amount < _amount
            ) {
                IbetStraightBond(order.token).transfer(
                    msg.sender,
                    balanceOf(msg.sender, order.token)
                );
                setBalance(msg.sender, order.token, 0);
                return false;
            }
        }

        // 更新処理：約定IDをカウントアップ => 約定情報を挿入する
        uint256 agreementId = latestAgreementId(_orderId) + 1;
        setLatestAgreementId(_orderId, agreementId);
        uint256 expiry = block.timestamp + lockingPeriod;
        setAgreement(
            _orderId,
            agreementId,
            msg.sender,
            _amount,
            order.price,
            false,
            false,
            expiry
        );

        // 更新処理：元注文の数量を減らす
        setOrder(
            _orderId,
            order.owner,
            order.token,
            order.amount.sub(_amount),
            order.price,
            order.isBuy,
            order.agent,
            order.canceled
        );

        if (order.isBuy) {
            // 更新処理：買い注文に対して売り注文で応じた場合、売りの預かりを拘束
            setBalance(
                msg.sender,
                order.token,
                balanceOf(msg.sender, order.token).sub(_amount)
            );
            setCommitment(
                msg.sender,
                order.token,
                commitmentOf(msg.sender, order.token).add(_amount)
            );
            // イベント登録：約定
            emit Agree(
                order.token,
                _orderId,
                agreementId,
                order.owner,
                msg.sender,
                order.price,
                _amount,
                order.agent
            );
        } else {
            // イベント登録：約定
            emit Agree(
                order.token,
                _orderId,
                agreementId,
                msg.sender,
                order.owner,
                order.price,
                _amount,
                order.agent
            );
        }

        return true;
    }

    /// @notice 決済承認
    /// @dev 注文時に指定された決済業者のみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 処理結果
    function confirmAgreement(
        uint256 _orderId,
        uint256 _agreementId
    ) public returns (bool) {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 指定した約定IDが、直近の約定ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());
        require(_agreementId <= latestAgreementId(_orderId));

        Order memory order;
        (
            order.owner,
            order.token,
            order.amount,
            order.price,
            order.isBuy,
            order.agent,
            order.canceled
        ) = getOrder(_orderId);

        Agreement memory agreement;
        (
            agreement.counterpart,
            agreement.amount,
            agreement.price,
            agreement.canceled,
            agreement.paid,
            agreement.expiry
        ) = getAgreement(_orderId, _agreementId);

        // <CHK>
        //  1) すでに決済承認済み（支払い済み）の場合
        //  2) すでに決済非承認済み（キャンセル済み）の場合
        //  3) 元注文で指定した決済業者ではない場合
        //   -> REVERT
        if (agreement.paid || agreement.canceled || msg.sender != order.agent) {
            revert();
        }

        // 更新処理：支払い済みフラグを支払い済み（True）に更新する
        setAgreement(
            _orderId,
            _agreementId,
            agreement.counterpart,
            agreement.amount,
            agreement.price,
            agreement.canceled,
            true,
            agreement.expiry
        );

        if (order.isBuy) {
            // 更新処理：買注文の場合、突合相手（売り手）から注文者（買い手）へと資産移転を行う
            setCommitment(
                agreement.counterpart,
                order.token,
                commitmentOf(agreement.counterpart, order.token).sub(
                    agreement.amount
                )
            );
            IbetStraightBond(order.token).transfer(
                order.owner,
                agreement.amount
            );
            // イベント登録：決済OK
            emit SettlementOK(
                order.token,
                _orderId,
                _agreementId,
                order.owner,
                agreement.counterpart,
                order.price,
                agreement.amount,
                order.agent
            );
        } else {
            // 更新処理：売注文の場合、注文者（売り手）から突合相手（買い手）へと資産移転を行う
            setCommitment(
                order.owner,
                order.token,
                commitmentOf(order.owner, order.token).sub(agreement.amount)
            );
            IbetStraightBond(order.token).transfer(
                agreement.counterpart,
                agreement.amount
            );
            // イベント登録：決済OK
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
        }

        // 更新処理：現在値を更新する
        setLastPrice(order.token, order.price);

        return true;
    }

    /// @notice 決済非承認
    /// @dev 注文時に指定された決済業者から実行が可能、有効期限後はMake注文者も実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 処理結果
    function cancelAgreement(
        uint256 _orderId,
        uint256 _agreementId
    ) public returns (bool) {
        // <CHK>
        //  1) 指定した注文番号が、直近の注文ID以上の場合
        //  2) 指定した約定IDが、直近の約定ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());
        require(_agreementId <= latestAgreementId(_orderId));

        Order memory order;
        (
            order.owner,
            order.token,
            order.amount,
            order.price,
            order.isBuy,
            order.agent,
            order.canceled
        ) = getOrder(_orderId);

        Agreement memory agreement;
        (
            agreement.counterpart,
            agreement.amount,
            agreement.price,
            agreement.canceled,
            agreement.paid,
            agreement.expiry
        ) = getAgreement(_orderId, _agreementId);

        if (agreement.expiry <= block.timestamp) {
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

        // 更新処理：キャンセル済みフラグをキャンセル（True）に更新する
        setAgreement(
            _orderId,
            _agreementId,
            agreement.counterpart,
            agreement.amount,
            agreement.price,
            true,
            agreement.paid,
            agreement.expiry
        );

        if (order.isBuy) {
            // 更新処理：買い注文の場合、突合相手（売り手）の預かりを解放 -> 預かりの引き出し
            // 取り消した注文は無効化する（注文中状態に戻さない）
            setCommitment(
                agreement.counterpart,
                order.token,
                commitmentOf(agreement.counterpart, order.token).sub(
                    agreement.amount
                )
            );
            IbetStraightBond(order.token).transfer(
                agreement.counterpart,
                agreement.amount
            );
            // イベント登録：決済NG
            emit SettlementNG(
                order.token,
                _orderId,
                _agreementId,
                order.owner,
                agreement.counterpart,
                order.price,
                agreement.amount,
                order.agent
            );
        } else {
            // 更新処理：元注文の数量を戻す
            setOrder(
                _orderId,
                order.owner,
                order.token,
                order.amount.add(agreement.amount),
                order.price,
                order.isBuy,
                order.agent,
                order.canceled
            );
            // イベント登録：決済NG
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
        }

        return true;
    }

    /// @notice 全ての残高を引き出しする
    /// @dev 未売却の預かりに対してのみ引き出しをおこなう。約定済、注文中の預かり（commitments）の引き出しはおこなわない。
    /// @param _token トークンアドレス
    /// @return 処理結果
    function withdrawAll(address _token) public returns (bool) {
        uint256 balance = balanceOf(msg.sender, _token);

        // <CHK>
        //  残高がゼロの場合、REVERT
        if (balance == 0) {
            revert();
        }

        // 更新処理：トークン引き出し（送信）
        IbetStraightBond(_token).transfer(msg.sender, balance);
        setBalance(msg.sender, _token, 0);

        // イベント登録
        emit Withdrawal(_token, msg.sender);

        return true;
    }

    /// @notice Deposit Handler：デポジット処理
    /// @param _from アカウントアドレス：残高を保有するアドレス
    /// @param _value デポジット数量
    function tokenFallback(
        address _from,
        uint _value,
        bytes memory /*_data*/
    ) public override {
        setBalance(_from, msg.sender, balanceOf(_from, msg.sender).add(_value));
    }

    /// @notice アドレスがコントラクトアドレスであるかを判定
    /// @param _addr アドレス
    /// @return is_contract 判定結果
    function isContract(address _addr) private view returns (bool is_contract) {
        uint length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    /// @notice Agentアドレスが有効なものであることをチェックする
    /// @param _addr アドレス
    /// @return 有効状態
    function validateAgent(address _addr) private view returns (bool) {
        return PaymentGateway(paymentGatewayAddress).getAgent(_addr);
    }
}
