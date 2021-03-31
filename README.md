<p align='center'>
  <img alt="ibet" src="https://user-images.githubusercontent.com/963333/71672471-6383c080-2db9-11ea-85b6-8815519652ec.png" width="300"/>
</p>

# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-21.3-blue.svg?cacheSeconds=2592000" />
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

## Running the tests

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

## Sponsors

[BOOSTRY Co., Ltd.](https://boostry.co.jp/)
