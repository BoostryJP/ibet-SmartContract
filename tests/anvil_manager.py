"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

import atexit
import os
import socket
import subprocess
import time
from pathlib import Path

import pytest
from local_anvil_config import local_anvil_command

_ANVIL_PROCESS: subprocess.Popen[str] | None = None


def _anvil_host() -> str:
    return os.environ.get("ANVIL_HOST", "127.0.0.1")


def _anvil_port() -> int:
    return int(os.environ.get("ANVIL_PORT", "8545"))


def _anvil_log_file() -> Path:
    return Path(os.environ.get("ANVIL_LOG_FILE", "/tmp/ibet-smartcontract-anvil.log"))


def _anvil_startup_timeout() -> int:
    return int(os.environ.get("ANVIL_STARTUP_TIMEOUT_SECONDS", "30"))


def _listener_pid() -> str | None:
    port = str(_anvil_port())
    result = subprocess.run(
        ["lsof", "-tiTCP:" + port, "-sTCP:LISTEN"],
        capture_output=True,
        text=True,
        check=False,
    )
    pid = result.stdout.strip().splitlines()
    return pid[0] if pid else None


def _listener_command(pid: str) -> str:
    result = subprocess.run(
        ["ps", "-p", pid, "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _is_port_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((_anvil_host(), _anvil_port())) == 0


def _wait_for_anvil() -> None:
    deadline = time.time() + _anvil_startup_timeout()
    while time.time() < deadline:
        if _is_port_open():
            return
        time.sleep(1)

    log_tail = ""
    log_file = _anvil_log_file()
    if log_file.exists():
        log_tail = "\n" + "".join(log_file.read_text().splitlines(keepends=True)[-50:])
    raise RuntimeError(
        f"Anvil did not become ready within {_anvil_startup_timeout()}s.{log_tail}"
    )


def stop_managed_anvil() -> None:
    """Stop the managed Anvil process if it is running."""
    global _ANVIL_PROCESS

    if _ANVIL_PROCESS is None:
        return

    _ANVIL_PROCESS.terminate()
    try:
        _ANVIL_PROCESS.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _ANVIL_PROCESS.kill()
        _ANVIL_PROCESS.wait(timeout=5)

    _ANVIL_PROCESS = None


def ensure_anvil_running() -> None:
    """Ensure that an Anvil process is running and ready to accept connections."""
    global _ANVIL_PROCESS

    # Check if anvil is already running on the specified port
    existing_pid = _listener_pid()
    if existing_pid is not None:
        existing_command = _listener_command(existing_pid)
        if "anvil" not in existing_command:
            raise RuntimeError(
                f"Port {_anvil_port()} is already in use by a non-anvil process: {existing_command}"
            )
        return

    # Start a new anvil process
    log_file = _anvil_log_file()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_file.open("w")
    _ANVIL_PROCESS = subprocess.Popen(
        local_anvil_command(host=_anvil_host(), port=_anvil_port()),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    _wait_for_anvil()
    atexit.register(stop_managed_anvil)


@pytest.hookimpl(tryfirst=True)
def pytest_configure():
    """Pytest hook to ensure Anvil is running before any tests are executed."""
    ensure_anvil_running()


@pytest.hookimpl(trylast=True)
def pytest_unconfigure():
    """Pytest hook to stop the managed Anvil process after all tests have completed."""
    stop_managed_anvil()
