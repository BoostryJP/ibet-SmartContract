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

import json
from pathlib import Path

BUILD_MANIFEST = Path(".build/__local__.json")
OUTPUT_DIR = Path("output")


def _iter_project_contracts(manifest):
    for name, contract in manifest.get("contractTypes", {}).items():
        source_id = contract.get("sourceId", "")
        if not source_id.startswith("contracts/"):
            continue

        yield name, contract


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for existing_file in OUTPUT_DIR.glob("*.json"):
        existing_file.unlink()

    with BUILD_MANIFEST.open("r", encoding="utf-8") as file:
        manifest = json.load(file)

    for name, contract_json in _iter_project_contracts(manifest):
        output = {"abi": contract_json["abi"]}

        deployment = contract_json.get("deploymentBytecode", {})
        runtime = contract_json.get("runtimeBytecode", {})
        if "bytecode" in deployment:
            output["bytecode"] = deployment["bytecode"]
        if "bytecode" in runtime:
            output["deployedBytecode"] = runtime["bytecode"]

        with (OUTPUT_DIR / f"{name}.json").open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=2)


if __name__ == "__main__":
    main()
