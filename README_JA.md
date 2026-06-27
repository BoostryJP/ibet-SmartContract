<p align="center">
  <img width="33%" src="https://user-images.githubusercontent.com/963333/71672471-6383c080-2db9-11ea-85b6-8815519652ec.png"/>
</p>

# ibet Smart Contract

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-26.6-blue.svg?cacheSeconds=2592000" />
  <img alt="License: Apache--2.0" src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" />
</p>

[English](README.md) | 日本語

**ibet ネットワーク上で利用可能なトークンおよびDEXコントラクト実装**

## プロジェクトの概要
- ibet-SmartContract プロジェクトは [ibet-Network blockchain](https://github.com/BoostryJP/ibet-Network) 上にオープンな金融システムを構築するプロジェクトです。
- このプロジェクトでは、ibet-Network 上で利用可能なトークン規格、分散取引所、あるいはその他の有用なツール群などを提供することを目的にしています。

## 依存
- [Python3](https://www.python.org/downloads/)
  - バージョン 3.14
- [uv](https://docs.astral.sh/uv/)
  - Python 環境の管理と Ape コマンドの実行には uv を利用しています。
- [Solidity](https://docs.soliditylang.org/)
  - スマートコントラクトの実装には Solidity を利用しています。
  - 現在、私たちは v0.8.34 を利用しています。
- [Ape](https://apeworx.io/)
  - コントラクトのコンパイルとテストには Ape を利用しています。
- [Foundry Anvil](https://www.getfoundry.sh/anvil)
  - ローカル開発・ユニットテストでは Anvil を利用しています。
- [OpenZeppelin](https://openzeppelin.com/contracts/)
  - 私たちのプロジェクトの一部は OpenZeppelin に依存しています。
  - openzeppelin-contracts の v4.9.3 を利用しています。
- [Node.js](https://nodejs.org/en/download/)
  - バージョン 24
  
## 各コントラクトの概要

### インターフェース: `/interfaces`

- `IbetStandardTokenInterface`: ibetトークンコントラクトの標準インターフェース
- `IbetExchangeInterface`: 取引所コントラクトの標準インターフェース

### コントラクト: `/contracts`

- **access**: オーナーシップやアクセス制御の基本コントラクト（例: `Ownable`）
- **exchange**: 分散型取引所やエスクロー、DVPなどの取引・決済関連コントラクト（`IbetExchange`、`IbetEscrow`、`IbetSecurityTokenDVP` など）
- **ledger**: オンチェーンアカウントとオフチェーン情報を紐付ける個人情報管理コントラクト（`PersonalInfo`）
- **payment**: トークンとオフチェーン決済のアトミックな受渡しを実現するペイメントゲートウェイ・DvPエージェントコントラクト（`PaymentGateway`）
- **token**: 各種トークン標準および実装：
  - ibet独自トークン（Bond型、Share型、Membership型、Coupon型）
  - ERC20・ERC721互換トークン
  - トークンレジストリコントラクト（`TokenList`）
- **utils**: メッセージング、コントラクトウォレットなどの補助コントラクト群（`E2EMessaging`、`SnapMessaging`、`P256Wallet` など）

## インストール

Python、Node.js、および開発用依存関係をインストールします。
事前に `uv` と Foundry が利用できる状態になっていることを確認してください。
```bash
$ make install
```

Ape が管理する Solidity パッケージ依存関係をインストールします。
```bash
$ make setup
```

## コントラクトのコンパイル

Ape を利用してコントラクトをコンパイルします。
```bash
$ make compile
```

必要に応じて、以下のコマンドを直接実行することもできます。

```bash
$ uv run ape compile
```

## スマートコントラクトの開発

### ローカル開発環境

ローカルのテストネットワークは `ethereum:local:foundry` を利用します。
Ape の設定は `ape-config.yaml` に定義されており、pytest でも同じネットワークがデフォルトで利用されます。

### テストの実行

全テストを実行する場合は、以下のコマンドを利用します。
```bash
$ make test
```

必要に応じて、Ape のコマンドを直接実行することもできます。

```bash
$ uv run ape test --network ethereum:local:foundry tests/
```

開発中に一部のテストだけを実行したい場合は、`ARG` で pytest の対象を渡せます。

```bash
$ make test ARG="tests/token/test_IbetERC20.py"
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
