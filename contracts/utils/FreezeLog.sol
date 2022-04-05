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

/// @title Freeze Log
contract FreezeLog {
    // Event: log recorded
    event Recorded(
        address indexed recorder,
        uint256 index,
        uint256 _freezingGraceBlockCount
    );

    // Event: log updated
    event Updated(address indexed recorder, uint256 index);

    struct Log {
        address recorder; // Recorder
        string log; // Log text
        uint256 createdBlockNumber; // Created block number
        uint256 freezingGraceBlockCount; // Freezing grace block count
    }

    /// Recorder -> Index
    mapping(address => uint256) public last_log_index;
    /// Recorder -> Index -> Log
    mapping(address => mapping(uint256 => Log)) public logs;

    // [CONSTRUCTOR]
    constructor() {}

    /// @notice Get last index
    /// @param _recorder Recorder
    /// @return _index Last index
    function lastLogIndex(address _recorder)
        public
        view
        returns (uint256 _index)
    {
        return last_log_index[_recorder];
    }

    /// @notice Record new logs
    /// @param _log Log text
    /// @param _freezingGraceBlockCount Freezing grace block count
    function recordLog(string memory _log, uint256 _freezingGraceBlockCount)
        public
    {
        Log storage log = logs[msg.sender][last_log_index[msg.sender]];

        log.recorder = msg.sender;
        log.log = _log;
        log.createdBlockNumber = block.number;
        log.freezingGraceBlockCount = _freezingGraceBlockCount;
        last_log_index[msg.sender]++;

        emit Recorded(
            msg.sender,
            last_log_index[msg.sender] - 1,
            _freezingGraceBlockCount
        );
    }

    /// @notice Update recorded logs
    /// @param _index Index
    /// @param _log Log to be updated
    function updateLog(uint256 _index, string memory _log) public {
        Log storage storageLog = logs[msg.sender][_index];

        require(
            storageLog.createdBlockNumber +
                storageLog.freezingGraceBlockCount >=
                block.number,
            "frozen"
        );

        storageLog.log = _log;

        emit Updated(msg.sender, _index);
    }

    /// @notice Get log
    /// @param _recorder Recorder
    /// @param _index Index
    function getLog(address _recorder, uint256 _index)
        public
        view
        returns (
            uint256 _createdBlockNumber,
            uint256 _freezingGraceBlockCount,
            string memory _log
        )
    {
        Log storage log = logs[_recorder][_index];
        return (log.createdBlockNumber, log.freezingGraceBlockCount, log.log);
    }
}
