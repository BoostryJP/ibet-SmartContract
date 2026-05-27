<p align="center">
  <img width="33%" src="https://user-images.githubusercontent.com/963333/71672471-6383c080-2db9-11ea-85b6-8815519652ec.png"/>
</p>

# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-26.6-blue.svg?cacheSeconds=2592000" />
  <img alt="License: Apache--2.0" src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" />
</p>

English | [日本語](README_JA.md)

**Tokens and DEX contracts available in the ibet DeFi network**

## Features
- The ibet-SmartContract project is a project to build an open financial system on the [ibet-Network blockchain](https://github.com/BoostryJP/ibet-Network).
- The project aims to provide token standards, decentralized exchanges, and other utility functions that can be used on the ibet-Network.

## Dependencies
- [Python3](https://www.python.org/downloads/)
  - Version 3.13
- [uv](https://docs.astral.sh/uv/)
  - We use uv to manage the Python environment and run Ape commands.
- [Solidity](https://docs.soliditylang.org/)
  - We are using Solidity to implement our smart contracts.
  - Currently, we are using v0.8.34.
- [Ape](https://apeworx.io/)
  - We use Ape as the primary framework for compiling and testing contracts.
- [Foundry Anvil](https://www.getfoundry.sh/anvil)
  - We use Anvil for local development and unit testing.
- [OpenZeppelin](https://openzeppelin.com/contracts/)
  - Our project is partly dependent on OpenZeppelin.
  - We use openzeppelin-contracts v4.9.3.
- [Node.js](https://nodejs.org/en/download/)
  - Version 24
  
## Overview

### Interface: `/interfaces`

- `IbetStandardTokenInterface`: Standard interface for ibet token contracts
- `IbetExchangeInterface`: Standard interface for exchange contracts

### Contracts: `/contracts`

- **access**: Ownership and access control primitives (e.g., `Ownable`)
- **exchange**: Decentralized exchange and escrow contracts, including DVP (`IbetExchange`, `IbetEscrow`, `IbetSecurityTokenDVP`, etc.)
- **ledger**: Personal information registry for associating off-chain data with on-chain accounts (`PersonalInfo`)
- **payment**: Payment gateway and DvP agent contracts for atomic settlement between tokens and off-chain payments (`PaymentGateway`)
- **token**: Various token standards and implementations:
  - ibet original tokens (Bond, Share, Membership, Coupon)
  - ERC20 and ERC721 compatible tokens
  - Token registry contract (`TokenList`)
- **utils**: Utility contracts for messaging, contract wallet, etc. (`E2EMessaging`, `SnapMessaging`, `P256Wallet`, etc.)

## Install

Install Python, Node.js, and development dependencies.
Make sure `uv` and Foundry are available in your environment before running the setup commands.

```bash
$ make install
```

Install Solidity package dependencies managed by Ape.

```bash
$ make setup
```

## Compile Contracts
Compile contracts with Ape.

```bash
$ make compile
```

You can also run the underlying command directly.

```bash
$ uv run ape compile
```

## Developing Smart Contracts

### Local setup

The default local test network is `ethereum:local:foundry`.
The Ape configuration is defined in `ape-config.yaml`, and pytest uses the same network by default.

### Running the tests

Run the full test suite with:

```bash
$ make test
```

You can also run the underlying Ape command directly.

```bash
$ uv run ape test --network ethereum:local:foundry tests/
```

If you need a narrower run during development, pass pytest targets through `ARG`.

```bash
$ make test ARG="tests/token/test_IbetERC20.py"
```

## Branching model

This repository is version controlled using the following flow.

<p align='center'>
  <img alt="ibet" src="https://user-images.githubusercontent.com/963333/161243132-5216b4f0-cbc6-443f-bcfc-9eafb4858cb1.png"/>
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
