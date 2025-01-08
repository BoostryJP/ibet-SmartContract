<p align="center">
  <img width="33%" src="https://user-images.githubusercontent.com/963333/71672471-6383c080-2db9-11ea-85b6-8815519652ec.png"/>
</p>

# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-24.12-blue.svg?cacheSeconds=2592000" />
  <img alt="License: Apache--2.0" src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" />
</p>

[English](README.md) | 日本語

**ibet ネットワーク上で利用可能なトークンおよびDEXコントラクト実装**

## プロジェクトの概要
- ibet-SmartContract プロジェクトは [ibet-Network blockchain](https://github.com/BoostryJP/ibet-Network) 上にオープンな金融システムを構築するプロジェクトです。
- このプロジェクトでは、ibet-Network 上で利用可能なトークン規格、分散取引所、あるいはその他の有用なツール群などを提供することを目的にしています。

## 依存
- [Python3](https://www.python.org/downloads/)
  - バージョン 3.11
- [Node.js](https://nodejs.org/en/download/)
  - バージョン 20
- [Solidity](https://docs.soliditylang.org/)
  - スマートコントラクトの実装には Solidity を利用しています。
  - 現在、私たちは v0.8.23 を利用しています。
- [eth-brownie](https://github.com/eth-brownie/brownie)
  - eth-brownie フレームワークを利用して、コントラクトの開発とテストを行なっています。
- [GoQuorum](https://github.com/ConsenSys/quorum)
  - [ibet-Network](https://github.com/BoostryJP/ibet-Network) の公式の GoQuorum ノード上での動作をサポートしています。
  - ローカル開発・テストでは [hardhat network](https://hardhat.org/hardhat-network/) を利用しています。最新バージョンを利用しています。
- [OpenZeppelin](https://openzeppelin.com/contracts/)
  - 私たちのプロジェクトの一部は OpenZeppelin に依存しています。
  - openzeppelin-contracts の v4.9 を利用しています。
  
## 各コントラクトの概要

### インターフェース: `/interfaces`

- `IbetStandardTokenInterface`: トークンの標準インターフェース
- `IbetExchangeInterface`: 取引（Exchange）コントラクトの標準インターフェース

### コントラクト: `/contracts`

- `access`: 各アクションを実行できるユーザーを決定するための権限制御機能を提供します。
- `exchange`: 様々な取引機能（Exchange）の実装です。
- `ledger`: 法定原簿に必要な付加情報を管理するためのデータストレージ機能を提供します。
- `payment`: オフチェーン決済を実現するため機能群です。
- `token`: 各種トークンフォーマットの実装です（ERC20、ERC721、Bond型、Share型など）。
- `utils`: その他のユーティリティ機能です。

## インストール

eth-brownie をインストールします。
```bash
$ make install
```

openzeppelin-contractsをインストールします。
```bash
$ brownie pm install OpenZeppelin/openzeppelin-contracts@4.9.3
```

hardhatをインストールします。
```bash
$ npm install
```

## コントラクトのコンパイル

コントラクトのコンパイルには eth-brownie を利用します。
```bash
$ brownie compile
```

## コントラクトのデプロイ

### 環境変数の設定

コントラクトデプロイ時に用いるEOAを、環境変数で切り替えることができます。

#### 1. GoQuorum (Geth)

GoQuorum（Geth）内に保存した秘密鍵を仕様する場合は、以下の環境変数を設定してください。

- `ETH_ACCOUNT_PASSWORD` - Geth の keystore file に設定したパスフレーズ

#### 2. ローカルの keystore file

ローカルに保存した keystore file を利用する場合は、以下の環境変数を設定してください。

- `ETH_KEYSTORE_PATH` - keystore file を保存したディレクトリパス。
- `ETH_ACCOUNT_PASSWORD` - keystore file に設定したパスフレーズ

#### 3. 平文の秘密鍵

平文の秘密鍵を利用する場合は、以下の環境変数を設定してください。

- `ETH_PRIVATE_KEY` - 平文の秘密鍵
- `ETH_ACCOUNT_PASSWORD` - 秘密鍵を暗号化するためのパスフレーズ

#### 4. AWS Secrets Manager

[AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html) に保存した秘密鍵を指定することもできます。
秘密鍵は keystore file のフォーマットで保存してください。
以下の環境変数を設定してください。

- `AWS_REGION_NAME` - AWS リージョン（デフォルト：ap-northeast-1）
- `AWS_SECRETS_ID` - シークレットの ARN
- `ETH_ACCOUNT_PASSWORD` - keystore file に対して設定したパスフレーズ

### コントラクトのデプロイ方法

以下のコマンドを実行してコントラクトのデプロイが可能です。

```bash
$ ./scripts/deploy_shared_contract.sh {--payment_gateway 0xabcd...} {contract_name}
```

`contract_name` として、以下のコントラクトをデプロイすることができます。

- E2EMessaging 
- TokenList
- PersonalInfo
- PaymentGateway
- IbetExchange (* --payment_gateway オプションが必要)
- IbetEscrow
- IbetSecurityTokenEscrow
- FreezeLog

その他のコントラクトはスクリプトによるデプロイをサポートしていません。
それらのコントラクトについては、その他の方法でデプロイする必要があります。

## スマートコントラクトの開発

### ネットワーク（hardhat）の設定

ネットワーク設定は `hardhat.config.js` ファイルに定義されています。

- chainId: 2017
- gasPrice: 0
- blockGasLimit: 800000000
- hardfork: "berlin"

ローカル環境で開発を行う際は、`docker-compose.yml` に定義されている、`hardhat-network` コンテナを起動して利用してください。
デフォルトでは 8545 ポートで RPC サービスが起動します。

### Brownie の設定

ネットワーク設定を Brownie にインポートします。
```bash
$ brownie networks import data/networks.yml
```

### テストの実行

以下のようにテストを実行します。
```bash
$ brownie test
```

以下のように pytest を利用することも可能です。
```bash
$ pytest tests/
```

## ブランチ作成方針

このリポジトリは以下の図で示されるフローでバージョン管理が行われています。

<p align='center'>
  <img alt="ibet" src="https://user-images.githubusercontent.com/963333/161243132-5216b4f0-cbc6-443f-bcfc-9eafb4858cb1.png"/>
</p>


## ライセンス

ibet-SmartContract は Apache License, Version 2.0 でライセンスされています。


## 連絡先

私たちは、皆様のユースケースをサポートするために、オープンソースに取り組んでいます。 私たちは、あなたがこのライブラリをどのように使用し、どのような問題の解決に役立っているかを知りたいと思います。 私たちは、2つのコミュニケーション用の手段を用意しています。

- [public discussion group](https://github.com/BoostryJP/ibet-SmartContract/discussions) では、ロードマップ、アップデート、イベント等を共有します。
- [dev@boostry.co.jp](mailto:dev@boostry.co.jp) のEメール宛に連絡をいただければ、直接私たちに連絡することができます。

機密事項の送信はご遠慮ください。過去に送信したメッセージの削除を希望される場合は、ご連絡ください。

## スポンサー

[BOOSTRY Co., Ltd.](https://boostry.co.jp/)
