# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-21.12-blue.svg?cacheSeconds=2592000" />
  <img alt="License: Apache--2.0" src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" />
</p>

<img width="33%" align="right" src="https://user-images.githubusercontent.com/963333/71672471-6383c080-2db9-11ea-85b6-8815519652ec.png"/>

**Tokens and DEX contracts available in the ibet DeFi network**

## Features
- The ibet-SmartContract project is a project to build an open financial system on the [ibet-Network blockchain](https://github.com/BoostryJP/ibet-Network).
- The project aims to provide token standards, decentralized exchanges, and other utility functions that can be used on the ibet-Network.

## Dependencies
- [python3](https://www.python.org/downloads/release/python-368/)
  - Version 3.6 or greater
- [eth-brownie](https://github.com/eth-brownie/brownie)
  - We are using the eth-brownie framework for developing and testing our contracts.
- [GoQuorum](https://github.com/ConsenSys/quorum)
  - We support the official GoQuorum node of [ibet-Network](https://github.com/BoostryJP/ibet-Network).
  - We use [ganache-cli](https://github.com/trufflesuite/ganache-cli) for local development and unit testing, and we use the latest version.
- [OpenZeppelin](https://openzeppelin.com/contracts/)
  - Our project is partly dependent on OpenZeppelin.
  - We use openzeppelin-contracts v4.2.
  
## Overview

### Interface: `/interfaces`

- `IbetStandardTokenInterface`: Standard token interface for ibet-SmartContract
- `IbetExchangeInterface`: Standard interface for exchange contracts in ibet-SmartContract.

### Contract: `/contracts`

- `access`: Determines which users can perform each action in the system.
- `exchange`: Implementations of the various exchanges.
- `ledger`: A data storage system that manages the data required as additional information in the ledger.
- `payment`: A set of functions required to build an off-chain payment system.
- `token`: Implementation of the various token formats: Bonds, Shares, etc.
- `utils`: A set of other utility functions.

## Install

Install eth-brownie as a python package.

```bash
$ pip install -r requirements.txt
```

Install openzeppelin-contracts.

```bash
$ brownie pm install OpenZeppelin/openzeppelin-contracts@4.2.0
```

## Compile Contracts
Use eth-brownie to compile contracts.

```bash
$ brownie compile
```

## Deploy Contracts

### Setting environment variables

You can switch the EOA used for deploying the contract by setting an environment variable.

#### 1. GoQuorum (Geth)

This is the case when you store and use your private key in Geth.

- `ETH_ACCOUNT_PASSWORD` - The passphrase you have set for the Geth keystore file.

#### 2. Local keystore file

This is the case when you use a local keystore file.

- `ETH_KEYSTORE_PATH` - Path of the directory where the keystore is stored.
- `ETH_ACCOUNT_PASSWORD` - The passphrase you have set for the keystore file.

#### 3. Raw private key

This is the case when you use a raw private key.

- `ETH_PRIVATE_KEY` - Raw private key
- `ETH_ACCOUNT_PASSWORD` - Passphrase for encrypting the private key.

#### 4. AWS Secrets Manager

This is the case of storing and using a private key in keystore file format in [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html).

- `AWS_REGION_NAME` - AWS Region (default: ap-northeast-1)
- `AWS_SECRETS_ID` - Secret's ARN
- `ETH_ACCOUNT_PASSWORD` - The passphrase you have set for the keystore file.

### How to deploy contracts
To deploy, execute the following command.

```bash
$ ./scripts/deploy_shared_contract.sh {--payment_gateway 0xabcd...}
```

## Developing Smart Contracts

### Ganache settings

#### Server
* hostname : 127.0.0.1 - lo0
* port number : 8545
* chain id : 2017

#### Chain
* gas price : 0
* hard fork : Petersburg

### Brownie settings

Importing network settings to Brownie.

```bash
$ brownie networks import data/networks.yml
```

### Running the tests

You can run the tests with:
```bash
$ brownie test
```

Alternatively, you can use pytest and run it as follows.
```bash
$ pytest tests/
```

## Branching model

<p align='center'>
  <img alt="ibet" src="https://user-images.githubusercontent.com/963333/128963415-df122a46-b813-4832-a64e-7830a175f825.png"/>
</p>


## License

ibet-SmartContract is licensed under the Apache License, Version 2.0.


## Contact information

We are committed to open-sourcing our work to support your use cases. 
We want to know how you use this library and what problems it helps you to solve. 
We have two communication channels for you to contact us:

* A [public discussion group](https://github.com/BoostryJP/ibet-SmartContract/discussions)
where we will also share our preliminary roadmap, updates, events, and more.

* A private email alias at
[dev@boostry.co.jp](mailto:dev@boostry.co.jp)
where you can reach out to us directly about your use cases and what more we can
do to help and improve the library.
  
Please refrain from sending any sensitive or confidential information. 
If you wish to delete a message you've previously sent, please contact us.


## Sponsors

[BOOSTRY Co., Ltd.](https://boostry.co.jp/)
