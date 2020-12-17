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

pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

import "./SafeMath.sol";
import "./Ownable.sol";
import "../interfaces/IbetStandardTokenInterface.sol";
import "./OTCExchangeStorageModel.sol";
import "./OTCExchangeStorage.sol";
import "./PaymentGateway.sol";
import "./PersonalInfo.sol";
import "./RegulatorService.sol";


/// @title ibet OTC DEX
contract IbetOTCExchange is Ownable, OTCExchangeStorageModel {
    using SafeMath for uint256;

    /// 約定明細の有効期限
    /// 現在の設定値は14日で設定している（長期の連休を考慮）
    uint256 lockingPeriod = 1209600;

    /// ---------------------------------------------------------------
    /// Event
    /// ---------------------------------------------------------------

    /// Event：注文
    event NewOrder(
        address indexed tokenAddress,
        uint256 orderId,
        address indexed ownerAddress,
        address indexed counterpartAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    /// Event: 注文取消
    event CancelOrder(
        address indexed tokenAddress,
        uint256 orderId,
        address indexed ownerAddress,
        address indexed counterpartAddress,
        uint256 price,
        uint256 amount,
        address agentAddress
    );

    /// Event: 約定
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

    /// Event: 決済OK
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

    /// Event: 決済NG
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

    /// Event: 全引き出し
    event Withdrawal(
        address indexed tokenAddress,
        address indexed accountAddress
    );

    /// ---------------------------------------------------------------
    /// Constructor
    /// ---------------------------------------------------------------
    address public personalInfoAddress;
    address public paymentGatewayAddress;
    address public storageAddress;
    address public regulatorServiceAddress;

    /// [CONSTRUCTOR]
    /// @param _paymentGatewayAddress PaymentGatewayコントラクトアドレス
    /// @param _personalInfoAddress PersonalInfoコントラクトアドレス
    /// @param _storageAddress OTCExchangeStorageコントラクトアドレス
    /// @param _regulatorServiceAddress RegulatorServiceコントラクトアドレス
    constructor(
        address _paymentGatewayAddress,
        address _personalInfoAddress,
        address _storageAddress,
        address _regulatorServiceAddress
    )
        public
    {
        paymentGatewayAddress = _paymentGatewayAddress;
        personalInfoAddress = _personalInfoAddress;
        storageAddress = _storageAddress;
        regulatorServiceAddress = _regulatorServiceAddress;
    }

    /// -------------------------------------------------------------------
    /// Function: getter/setter
    /// -------------------------------------------------------------------

    /// @notice 注文情報取得
    /// @param _orderId 注文ID
    /// @return _owner 注文実行者（売り手）アドレス
    /// @return _counterpart 取引相手（買い手）アドレス
    /// @return _token トークンアドレス
    /// @return _amount 注文数量
    /// @return _price 注文単価
    /// @return _agent 決済業者のアドレス
    /// @return _canceled キャンセル済み状態
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
        OTCExchangeStorageModel.OTCOrder memory _order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

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

    /// @notice 注文情報更新
    /// @param _orderId 注文ID
    /// @param _owner 注文実行者（売り手）アドレス
    /// @param _counterpart 取引相手（買い手）アドレス
    /// @param _token トークンアドレス
    /// @param _amount 注文数量
    /// @param _price 注文単価
    /// @param _agent 決済業者のアドレス
    /// @param _canceled キャンセル済み状態
    /// @return 処理結果
    function setOrder(
        uint256 _orderId,
        address _owner,
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent,
        bool _canceled
    )
        private
        returns (bool)
    {
        OTCExchangeStorageModel.OTCOrder memory _order = OTCExchangeStorageModel.mappingOTCOrder(
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

    /// @notice 約定情報取得
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return _counterpart 約定相手（売り手）アドレス
    /// @return _amount 約定数量
    /// @return _price 約定単価
    /// @return _canceled キャンセル済み状態
    /// @return _paid 支払済状態
    /// @return _expiry 有効期限
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
        OTCExchangeStorageModel.OTCAgreement memory _agreement = OTCExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);
        return (
           _agreement.counterpart,
           _agreement.amount,
           _agreement.price,
           _agreement.canceled,
           _agreement.paid,
           _agreement.expiry
        );
    }

    /// @notice 約定情報更新
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _counterpart 約定相手（売り手）アドレス
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
    )
        private
        returns (bool)
    {
        OTCExchangeStorageModel.OTCAgreement memory _agreement = OTCExchangeStorageModel.mappingOTCAgreement(
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

    /// @notice 直近注文ID取得
    /// @return 直近注文ID
    function latestOrderId()
        public
        view
        returns (uint256)
    {
        return OTCExchangeStorage(storageAddress).getLatestOrderId();
    }

    /// @notice 直近注文ID更新
    /// @param _value 更新後の直近注文ID
    /// @return 処理結果
    function setLatestOrderId(uint256 _value)
        private
        returns (bool)
    {
        OTCExchangeStorage(storageAddress).setLatestOrderId(_value);
        return true;
    }

    /// @notice 直近約定ID取得
    /// @param _orderId 注文ID
    /// @return 直近約定ID
    function latestAgreementId(uint256 _orderId)
        public
        view
        returns (uint256)
    {
        return OTCExchangeStorage(storageAddress).getLatestAgreementId(_orderId);
    }

    /// @notice 直近約定ID更新
    /// @param _orderId 注文ID
    /// @param _value 更新後の直近約定ID
    /// @return 処理結果
    function setLatestAgreementId(uint256 _orderId, uint256 _value)
        private
        returns (bool)
    {
        OTCExchangeStorage(storageAddress).setLatestAgreementId(_orderId, _value);
        return true;
    }

    /// @notice 残高参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return OTCExchangeStorage(storageAddress).getBalance(
            _account,
            _token
        );
    }

    /// @notice 残高数量更新
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の残高数量
    /// @return 処理結果
    function setBalance(address _account, address _token, uint256 _value)
        private
        returns (bool)
    {
        return OTCExchangeStorage(storageAddress).setBalance(
            _account,
            _token,
            _value
        );
    }

    /// @notice 拘束数量参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 拘束数量
    function commitmentOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return OTCExchangeStorage(storageAddress).getCommitment(
            _account,
            _token
        );
    }

    /// @notice 拘束数量更新
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の拘束数量
    /// @return 処理結果
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

    /// ---------------------------------------------------------------
    /// Function: Logic
    /// ---------------------------------------------------------------

    /// @notice Make注文
    /// @param _counterpart 取引相手（買い手）アドレス
    /// @param _token トークンアドレス
    /// @param _amount 注文数量
    /// @param _price 注文単価
    /// @param _agent 収納代行業者のアドレス
    /// @return 処理結果
    function createOrder(
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent
    )
        public
        returns (bool)
    {
        // <CHK>
        //  取引参加者チェック
        if (regulatorServiceAddress != address(0)) {
            require(RegulatorService(regulatorServiceAddress).check(msg.sender) == 0 || RegulatorService(regulatorServiceAddress).check(_counterpart) == 0);
        }

        // <CHK>
        //  1) 注文数量が0の場合
        //  2) 残高数量が発注数量に満たない場合
        //  3) 名簿用個人情報が登録されていない場合
        //  4) 取扱ステータスがFalseの場合
        //  5) 有効な収納代行業者（Agent）を指定していない場合
        //   -> 更新処理: 全ての残高を投資家のアカウントに戻し、falseを返す
        if (
            _amount == 0 ||
            balanceOf(msg.sender, _token) < _amount ||
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

    /// @notice 注文キャンセル
    /// @param _orderId 注文ID
    /// @return 処理結果
    function cancelOrder(uint256 _orderId)
        public
        returns (bool)
    {
        // <CHK>
        //  指定した注文番号が、直近の注文ID以上の場合
        //   -> REVERT
        require(_orderId <= latestOrderId());

        OTCExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        // <CHK>
        //  1) 元注文の残注文数量が0の場合
        //  2) 注文がキャンセル済みの場合
        //  3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
        //  4) 取扱ステータスがFalseの場合
        //   -> REVERT
        if (
            order.amount == 0 ||
            order.canceled == true ||
            order.owner != msg.sender ||
            IbetStandardTokenInterface(order.token).status() == false
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

    /// @notice Take注文
    /// @dev 約定数量 = 注文数量
    /// @param _orderId 注文ID
    /// @return 処理結果
    function executeOrder(uint256 _orderId)
        public
        returns (bool)
    {
        // <CHK>
        //  指定した注文IDが直近の注文IDを超えている場合
        require(_orderId <= latestOrderId());

        OTCExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        // <CHK>
        //  取引参加者チェック
        if (regulatorServiceAddress != address(0)) {
            require(
                RegulatorService(regulatorServiceAddress).check(msg.sender) == 0 ||
                RegulatorService(regulatorServiceAddress).check(order.owner) == 0
            );
        }

        // <CHK>
        //  取引関係者限定
        require(
            order.owner == msg.sender ||
            order.counterpart == msg.sender ||
            order.agent == msg.sender
        );

        // <CHK>
        //  1) 元注文の発注者と同一のアドレスからの発注の場合
        //  2) 元注文がキャンセル済の場合
        //  3) 名簿用個人情報が登録されていない場合
        //  4) 買注文者がコントラクトアドレスの場合
        //  5) 取扱ステータスがFalseの場合
        //  6) 元注文の残注文数量が0の場合
        //   -> REVERT
        if (
            msg.sender == order.owner ||
            order.canceled == true ||
            PersonalInfo(personalInfoAddress).isRegistered(msg.sender,IbetStandardTokenInterface(order.token).owner()) == false ||
            isContract(msg.sender) == true ||
            IbetStandardTokenInterface(order.token).status() == false ||
            order.amount == 0
        ) {
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

    /// @notice 決済承認
    /// @dev 注文時に指定された決済業者のみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 処理結果
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

        OTCExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        OTCExchangeStorageModel.OTCAgreement memory agreement = OTCExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);

        // <CHK>
        //  1) すでに決済承認済み（支払い済み）の場合
        //  2) すでに決済非承認済み（キャンセル済み）の場合
        //  3) 元注文で指定した決済業者ではない場合
        //  4) 取扱ステータスがFalseの場合
        //   -> REVERT
        if (
            agreement.paid ||
            agreement.canceled ||
            msg.sender != order.agent ||
            IbetStandardTokenInterface(order.token).status() == false
        ) {
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

    /// @notice 決済非承認
    /// @dev 注文時に指定された決済業者から実行が可能、有効期限後はMake注文者も実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 処理結果
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

        OTCExchangeStorageModel.OTCOrder memory order = OTCExchangeStorage(storageAddress).getOrder(_orderId);

        OTCExchangeStorageModel.OTCAgreement memory agreement = OTCExchangeStorage(storageAddress).getAgreement(_orderId, _agreementId);

        if (agreement.expiry <= now) {
            // 約定明細の有効期限を超過している場合
            // <CHK>
            //  1) すでに決済承認済み（支払い済み）の場合
            //  2) すでに決済非承認済み（キャンセル済み）の場合
            //  3) msg.senderが、 決済代行（agent）、発注者（owner）、約定相手（counterpart）以外の場合
            //  4) 取扱ステータスがFalseの場合
            //   -> REVERT
            if (
                agreement.paid ||
                agreement.canceled ||
                (msg.sender != order.agent &&
                    msg.sender != order.owner &&
                    msg.sender != agreement.counterpart) ||
                IbetStandardTokenInterface(order.token).status() == false
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
                msg.sender != order.agent ||
                IbetStandardTokenInterface(order.token).status() == false
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

    /// @notice 全ての残高を引き出しする
    /// @dev 未売却の預かりに対してのみ引き出しをおこなう。約定済、注文中の預かり（commitments）の引き出しはおこなわない。
    /// @param _token トークンアドレス
    /// @return 処理結果
    function withdrawAll(address _token)
        public
        returns (bool)
    {
        uint256 balance = balanceOf(msg.sender, _token);

        // <CHK>
        //  1) 残高がゼロの場合、REVERT
        //  2) 取扱ステータスがFalseの場合
        if (balance == 0 || IbetStandardTokenInterface(_token).status() == false) {
            revert();
        }

        // 更新処理: トークン引き出し（送信）
        IbetStandardTokenInterface(_token).transfer(msg.sender, balance);
        setBalance(msg.sender, _token, 0);

        // イベント登録
        emit Withdrawal(_token, msg.sender);

        return true;
    }

    /// @notice Deposit Handler：デポジット処理
    /// @param _from アカウントアドレス：残高を保有するアドレス
    /// @param _value デポジット数量
    function tokenFallback(address _from, uint256 _value, bytes memory /*_data*/)
        public
    {
        setBalance(
            _from,
            msg.sender,
            balanceOf(_from, msg.sender).add(_value)
        );
    }

    /// @notice アドレスがコントラクトアドレスであるかを判定
    /// @param _addr アドレス
    /// @return is_contract 判定結果
    function isContract(address _addr)
        private
        view
        returns (bool is_contract)
    {
        uint256 length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    /// @notice Agentアドレスが有効なものであることをチェックする
    /// @param _addr アドレス
    /// @return 有効状態
    function validateAgent(address _addr)
        private
        view
        returns (bool)
    {
        return PaymentGateway(paymentGatewayAddress).getAgent(_addr);
    }
}
