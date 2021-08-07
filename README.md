# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-21.9-blue.svg?cacheSeconds=2592000" />
  <a href="#" target="_blank">
    <img alt="License: Apache--2.0" src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" />
  </a>
</p>


## Install
```bash
$ pip install -r requirements.txt
```

## Compile
Use Brownie to compile.

```bash
$ brownie compile
```

## Deploy

You can switch the EOA used for deploying the contract by setting an environment variable.

1. GETH
    * `ETH_ACCOUNT_PASSWORD` - EOA passphrase

2. Ethereum Keystore FILE
    * `ETH_KEYSTORE_PATH` - Path of the directory where the keystore is stored.
    * `ETH_ACCOUNT_PASSWORD` - EOA passphrase

3. Ethereum Raw Private Key
    * `ETH_PRIVATE_KEY` - 64 random hex characters
    * `ETH_ACCOUNT_PASSWORD` - Passphrase to be set for the EOA generated from the private key.

4. AWS Secrets Manager
    * `AWS_REGION_NAME` - AWS Region (default: ap-northeast-1)
    * `AWS_SECRETS_ID` - Secret's ARN
    * `ETH_ACCOUNT_PASSWORD` - EOA passphrase

To deploy, execute the following command.

```bash
$ ./scripts/deploy.sh
```

## Developing Smart Contracts

### Requirements
* Python(3.6)
* Ganache

### Setting up Ganache

#### Server
* hostname : 127.0.0.1 - lo0
* port number : 8545
* chain id : 2017

#### Chain
* gas price : 0
* hard fork : Petersburg

#### Importing network settings to Brownie

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
