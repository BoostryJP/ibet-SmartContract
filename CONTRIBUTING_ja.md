# 開発者ドキュメント（日本語）

## 0. 開発推奨環境
* OS: macOS 10.14 (Mojave)
* Homebrew
* python（3.6.8）
* Ganache

### Ganache 設定
#### Server
* hostname : 127.0.0.1 - lo0
* port number : 8545
* chain id : 2017

#### Chain
* gas price : 0
* hard fork : Petersburg

## 1. solidity compiler (solc) のインストール
* コンパイル時に自動でインストールされる。
* 現状、macOSでの自動インストールは非推奨となっているため手動インストールが確実。
* ビルド済みsolc v0.4.25がibet-SmartContractのリポジトリのbin配下に入っているので、実行権限を付与し `solc-v0.4.24` に名前を変更の上、 `~/.solcx/` へコピーする。

## 2. ganache-cliのインストール
* [ganache-cli](https://github.com/trufflesuite/ganache-cli) をインストールする。

```bash
$ npm install -g ganache-cli
```

## 3. 依存パッケージのインストール（pip）
* 依存パッケージをpipインストールする。

```bash
$ pip install -r requirements.txt
```

## 3. コントラクトコードのコンパイル
* コントラクトコード（Solidityコード）自体は、好きなエディタで実装して良い。
* 出来上がったコントラクトコードを `interfaces/`, `contracts/` ディレクトリ以下に格納していく。
* コードのコンパイルは `brownie` コマンド実行時に自動的に行われる。
* 明示的にコンパイルしたい場合は以下のコマンドを実行する。

```bash
$ brownie compile
```

* 実行結果（abi, bytecode, bytecode_runtime など）は `build/interfaces/`, `build/contracts/` に保存される。

## 4. テストの実行
* テストコードを `tests/` の中に格納して、以下を実行する。

```bash
$ brownie test
```


## 5. Ganache接続設定
* ローカル環境のGanacheに接続するために、以下のコマンドを実行して接続先を登録する。

```bash
$ brownie networks import data/networks.yml
```

*  `brownie` コマンドに `--network local_network` オプションを付けるとローカル環境のGanacheに対して処理が行われる。

```bash
# 例: ローカル環境下のGanacheに接続してコンソールを開く
brownie console --network local_network
```

