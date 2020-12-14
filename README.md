<p align='center'>
  <img alt="ibet" src="https://user-images.githubusercontent.com/963333/71672471-6383c080-2db9-11ea-85b6-8815519652ec.png" width="300"/>
</p>

# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-0.15-blue.svg?cacheSeconds=2592000" />
  <a href="#" target="_blank">
    <img alt="License: Apache--2.0" src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" />
  </a>
</p>


## Install
```bash
$ pip install -r requirements.txt
```

## Deploy
The EOA used to deploy the contract can be switched by setting environment variables.
1. from GETH
* ETH_ACCOUNT_PASSWORD - The first EOA passphrase.
2. from Ethereum Keystore FILE
* ETH_KEYSTORE_PATH - aaa
* ETH_ACCOUNT_PASSWORD - EOA passphrase.
3. from Ethereum Private Key
* ETH_PRIVATE_KEY - 64 random hex characters.
* ETH_ACCOUNT_PASSWORD - Passphrase to set for generated EOA.
4. from AWS Secrets Manager
* AWS_SECRETS_ID - Secrets's ARN.
* ETH_ACCOUNT_PASSWORD - EOA passphrase.
```bash
$ ./scripts/deploy.sh
```

## Running the tests

You can run the tests with:
```bash
$ brownie test
```
