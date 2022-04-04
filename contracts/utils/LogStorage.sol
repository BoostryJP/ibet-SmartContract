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

/// @title Log Storage
contract LogStorage {
    // ログレコード
    struct log {
        address from;                       // ログ出力元アドレス
        string message;                     // ログ本文
        uint256 createdBlockNumber;         // ログ出力時のブロックカウント数
        uint256 freezingGraceBlockCount;    // 凍結までのブロックカウント数
    }

    uint256 public nextIndex = 0;
    mapping(uint256 => log) public logs;

    // イベント：ログ書込み
    event Wrote(
        uint256 logIndex,
        address indexed logAuthorAddress,
        string message,
        uint256 createdBlockNumber,
        uint256 freezingGraceBlockCount
    );

    // イベント：ログ編集
    event Edited(
        uint256 logIndex,
        address indexed logAuthorAddress,
        string message
    );

    /// @dev ログが凍結されていないことをチェック
    /// @param _index チェック対象のログインデックス
    modifier onlyUnfrozen(uint256 _index) {
        require(
            logs[_index].createdBlockNumber + logs[_index].freezingGraceBlockCount >= block.number,
            "frozen"
        );
        _;
    }

    /// @dev 対象のログがmsg.senderによって作成されたことをチェック
    /// @param _index チェック対象のログインデックス
    modifier onlyAuthor(uint256 _index) {
        require(
            logs[_index].from == msg.sender,
            "Can be edited by the author."
        );
        _;
    }

    // [CONSTRUCTOR]
    constructor()  {}

    /// @notice ログ書込み
    /// @param _message ログ本文
    /// @param _freezingGraceBlockCount 凍結までのブロックカウント数
    function writeLog(string memory _message, uint256 _freezingGraceBlockCount) public returns (uint256 logIndex) {
        // ログレコードをストレージに追加
        logs[nextIndex] = log(msg.sender, _message, block.number, _freezingGraceBlockCount);

        // イベント登録
        emit Wrote(
            nextIndex,
            msg.sender,
            _message,
            block.number,
            _freezingGraceBlockCount
        );
        nextIndex += 1;
        return nextIndex - 1;
    }

    /// @notice ログ編集
    /// @param _index ログインデックス
    /// @param _message 編集後のログ本文
    function editLog(uint256 _index, string memory _message) public onlyUnfrozen(_index) onlyAuthor(_index) {
        logs[_index].message = _message;

        // イベント登録
        emit Edited(
            _index,
            msg.sender,
            _message
        );
    }

    /// @notice ログ取得
    /// @param _index ログインデックス
    function getLogByIndex(uint256 _index)
    public
    view
    returns (
        address from,
        string memory message,
        uint256 createdBlockNumber,
        uint256 freezingGraceBlockCount
    )
    {
        require(logs[_index].from != address(0), "Log of that index is not stored yet.");
        return (
        logs[_index].from,
        logs[_index].message,
        logs[_index].createdBlockNumber,
        logs[_index].freezingGraceBlockCount
        );
    }
}