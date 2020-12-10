"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed onan "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

import json
import os


def main():
    # Contract
    file_list = os.listdir("build/contracts")
    for file in file_list:
        contract_json = json.load(open(f"build/contracts/{file}", "r"))
        output = {
            "abi": contract_json["abi"],
            "bytecode": contract_json["bytecode"],
            "deployedBytecode": contract_json["deployedBytecode"]
        }
        with open(f"output/{file}", "w") as f:
            json.dump(output, f, indent=2)

    # Interface
    file_list = os.listdir("build/interfaces")
    for file in file_list:
        contract_json = json.load(open(f"build/interfaces/{file}", "r"))
        output = {
            "abi": contract_json["abi"]
        }
        with open(f"output/{file}", "w") as f:
            json.dump(output, f, indent=2)


if __name__ == '__main__':
    main()