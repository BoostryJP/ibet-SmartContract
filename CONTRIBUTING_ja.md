# 開発者ドキュメント（日本語）

## 0. 開発推奨環境
* OS: macOS 10.14 (Mojave)
* homebrewインストール済
* python（3.6.4）インストール済
* Quorum開発環境構築済（ibet-Quorum）

## 1. solidity compiler (solc) のインストール
* brew install を実施する。
* 現状、0.5系が入ってしまうため、バージョンダウンが必要。
* ビルド済みsolc v0.4.25がibet-SmartContractのリポジトリのbin配下に入っているので、実行権限付与の上、PATHを通して使う。（ex: /usr/local/bin/solc）

## 2. 依存パッケージのインストール（pip）
* 依存パッケージをpipインストールする。

```bash
$ pip install -r requirements.txt
```

## 3. コントラクトコードのコンパイル
* コントラクトコード（Solidityコード）自体は、好きなエディタで実装して良い。
* 出来上がったコントラクトコードを `contracts/` ディレクトリ以下に格納していく。
* コードのコンパイルは以下のコマンドを実行する。

```bash
$ populus compile
```

* 実行結果（abi, bytecode, bytecode_runtime など）は `build/contracts.json` に保存される。

## 4. テストの実行
* テスト実行はpytestで実行する。
* テストコードを `tests/` の中に格納して、`tests`が存在するディレクトリで以下を実行する。

```bash
$ pytest tests/
```
