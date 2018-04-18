# tmr-sc

## 1. 環境構築

### 1.1. 事前準備
* geth をインストールする。
* Python3.6の実行環境を整備する。

* solidity compiler (solc) をインストールする。

```
$ sudo apt-get install solc
$ solc --version
solc, the solidity compiler commandline interface
Version: 0.4.21+commit.dfe3193c.Linux.g++
```

### 1.2. 依存パッケージのインストール
* 依存パッケージをpipでインストールする。
* 補足：　populusをそのままインストールした場合、パッケージの依存関係の問題でpopulus実行時にエラーになることがある（参考：　https://github.com/ethereum/populus/issues/450）。

```
$ pip install -r requirements.txt
```

* 動作確認

```
$ populus
Usage: populus [OPTIONS] COMMAND [ARGS]...

  Populus

Options:
  -p, --project PATH  Specify a populus project directory
  -l, --logging TEXT  Specify the logging level.  Allowed values are
                      DEBUG/INFO or their numeric equivalents 10/20
  -h, --help          Show this message and exit.

Commands:
  chain    Manage and run ethereum blockchains.
  compile  Compile project contracts, storing their...
  config   Manage and run ethereum blockchains.
  deploy   Deploys the specified contracts to a chain.
  init     Generate project layout with an example...
  upgrade  Upgrade a project config, and if required...
```

## 2. コントラクトコードのコンパイル
* コントラクトコード（Solidityコード）自体は、好きなエディタで実装して良い。
* 出来上がったコントラクトコードを `contracts/` ディレクトリ以下に格納していく。
* コードのコンパイルは以下のコマンドを実行する。
* 実行結果（abi, bytecode, bytecode_runtime など）は `build/contracts.json` に保存される。

```
$ populus compile
> Found 7 contract source files
  - contracts/IbetStraightBond.sol
  - contracts/IbetStraightBondExchange.sol
  - contracts/Ownable.sol
  - contracts/PersonalInfo.sol
  - contracts/SafeMath.sol
  - contracts/TokenList.sol
  - contracts/WhiteList.sol
> Compiled 8 contracts
  - contracts/IbetStraightBond.sol:ContractReceiver
  - contracts/IbetStraightBond.sol:IbetStraightBond
  - contracts/IbetStraightBondExchange.sol:IbetStraightBondExchange
  - contracts/Ownable.sol:Ownable
  - contracts/PersonalInfo.sol:PersonalInfo
  - contracts/SafeMath.sol:SafeMath
  - contracts/TokenList.sol:TokenList
  - contracts/WhiteList.sol:WhiteList
> Wrote compiled assets to: build/contracts.json
```

## 3. テスト
* テスト実行はpytestで実行する。
* テストコードを `tests/` の中に格納して、以下を実行する。

```
$ py.test tests/
```

* Warningの出力をさせたくない場合は、以下のオプションをつける。

```
$ py.test tests/ --disable-pytest-warnings
```
