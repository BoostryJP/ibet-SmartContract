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

pragma solidity ^0.8.0;

/// @title OTCExchangeStorageのModel
contract OTCExchangeStorageModel {
    // OTC取引情報
    struct OTCOrder {
        address owner; // 取引実行者（売り手）EOAアドレス
        address counterpart; // 買い手EOAアドレス
        address token; // トークンアドレス
        uint256 amount; // 売却数量
        uint256 price; // 売却単価
        address agent; // 決済業者のEOAアドレス
        bool canceled; // キャンセル状態
    }

    // OTC取引合意情報
    struct OTCAgreement {
        address counterpart; // 売り手EOAアドレス
        uint256 amount; // 約定数量
        uint256 price; // 約定単価
        bool canceled; // キャンセル状態
        bool paid; // 支払い状態
        uint256 expiry; // 有効期限（約定から１４日）
    }

    /// @dev OTC取引情報のMapper
    /// @param _owner 取引実行者（売り手）EOAアドレス
    /// @param _counterpart 買い手EOAアドレス
    /// @param _token トークンアドレス
    /// @param _amount 売却数量
    /// @param _price 売却単価
    /// @param _agent 決済業者のEOAアドレス
    /// @param _canceled キャンセル状態
    /// @return OTCOrder 取引情報
    function mappingOTCOrder(
        address _owner,
        address _counterpart,
        address _token,
        uint256 _amount,
        uint256 _price,
        address _agent,
        bool _canceled
    ) internal returns (OTCOrder memory) {
        OTCOrder memory _order = OTCOrder(
            _owner,
            _counterpart,
            _token,
            _amount,
            _price,
            _agent,
            _canceled
        );
        return _order;
    }

    /// @dev OTC取引合意情報のMapper
    /// @param _counterpart 売り手EOAアドレス
    /// @param _amount 売却数量
    /// @param _price 売却単価
    /// @param _canceled キャンセル状態
    /// @param _paid 支払い状態
    /// @param _expiry 有効期限
    /// @return OTCAgreement 取引合意情報
    function mappingOTCAgreement(
        address _counterpart,
        uint256 _amount,
        uint256 _price,
        bool _canceled,
        bool _paid,
        uint256 _expiry
    ) internal returns (OTCAgreement memory) {
        OTCAgreement memory _agreement = OTCAgreement(
            _counterpart,
            _amount,
            _price,
            _canceled,
            _paid,
            _expiry
        );
        return _agreement;
    }
}
