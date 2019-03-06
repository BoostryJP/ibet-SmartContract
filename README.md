# tmr-sc

## 1. 環境構築 (Mac)

### 1.0.前提条件
* OS:　OSX
* homebrewがインストールされている


### 1.1. Python3.6の実行環境を整備する
* (参考：https://develtips.com/python/191)


### 1.2. geth をインストールする。
* (参考：https://qiita.com/tmrex7/items/912ec05eff02f7f76d30)


### 1.3. solidity compiler (solc) をインストールする。
* brew install すると0.5系が入ってしまう。
* 対策として、ビルド済みsolc v0.4.25がtmr-scのリポジトリのbin配下に入っているので、実行権限付与の上、PATHを通して使う。（ex: /usr/local/bin/solc）
* (参考：https://solidity.readthedocs.io/en/v0.4.21/installing-solidity.html)

```
$ sudo apt-get install solc
$ solc --version
solc, the solidity compiler commandline interface
Version: 0.4.21+commit.dfe3193c.Linux.g++
```
* pathを通すためのエイリアスの設定(例)
~/.bash_profile　に以下を追記する

```
alias solc='/usr/local/bin/solc'
```

追記したら、`source ~/.bash_profile` して、再度compile

* 疎通確認

```
$ solc --version
solc, the solidity compiler commandline interface
Version: 0.4.25+commit.59dbf8f1.Darwin.appleclang
```


### 1.4. tmr-scをgit cloneする。
```
$ git clone https://github.com/N-Village/tmr-sc.git
```


### 1.5. Pyenv (virtualenv)の環境を作る
* （参考：https://qiita.com/its/items/24f8b20aa2106819dfb3）
* 開発を行うディレクトリ(ex: tmr-sc) の上位ディレクトリで以下のコマンドを実行する

```
$ pyenv install 3.6.4
$ pyenv virtualenv 3.6.4 tmr-sc
```

* 開発を行うディレクトリで以下のコマンドを実行し、localの設定を行う
* これにより真っ新な環境になるので、そこで 手順1.6を行うとクリーンなインストールができる

```
$ pyenv local tmr-sc
``` 

* 環境の確認

```
$ pyenv versions
  system
  3.6.4
  3.6.4/envs/tmr-sc
* tmr-sc (set by /Users/*/tmr-sc/.python-version)
```


### 1.6. 依存パッケージのインストール
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



### 1.7. AWS CLIの導入ならびにECRにログイン
* ibet 開発AWSのECRのイメージを使うので、AWS CLIの導入ならびにECRにログインしておく
* ※事前にAWS Access Key IDとAWS Secret Access Key等の情報を入手しておく
* (参考：https://docs.aws.amazon.com/ja_jp/AmazonECR/latest/userguide/ECR_AWSCLI.html)

```
$ pip install awscli --upgrade --ignore-installed six
$ aws configure

AWS Access Key ID [None]: *************ID
AWS Secret Access Key [None]: ******************************KEY
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

* 以下のコマンドで返ってきた内容をコピーして入力すると、ログインができる

```
$ aws ecr get-login --no-include-email

docker login -u AWS -p password 
** 省略 **
https://aws_account_id.dkr.ecr.us-east-1.amazonaws.com
```



### 1.8. dockerインストール
* 公式サイトから Docker for Macをダウンロードしてインストールする(https://docs.docker.com/docker-for-mac/install/) 
* 正しくインストールされているか確認する

```
$docker version
Client:
 Version:      17.03.1-ce
 API version:  1.27
 Go version:   go1.7.5
 Git commit:   c6d412e
 Built:        Tue Mar 28 00:40:02 2017
 OS/Arch:      darwin/amd64

Server:
 Version:      17.03.1-ce
 API version:  1.27 (minimum version 1.12)
 Go version:   go1.7.5
 Git commit:   c6d412e
 Built:        Fri Mar 24 00:00:50 2017
 OS/Arch:      linux/amd64
 Experimental: true
```
* Docker for mac に入っている docker-composeを使うために以下を行う
* MAC用docker-compose.ymlを入手し、volumesを以下の例のように適宜変更する

```
 volumes:
      - /Users/*/quorum_data/v1:/eth
```

* docker-composeを起動する

```
$ docker-compose up -d
```

※　ファイル名を変更した場合は、代わりに以下のコマンドを事項

```
$ docker-compose -f ファイル名 up -d
```

* 疎通確認

```
$ docker-compose --version
docker-compose version 1.23.2, build 1110ad01
```

### 1.9. Quorumのバリデーターの用意
* 初回のみ4つのロールアカウント（発行体、決済代行、投資家、開発コミュニティ）をgethで生成する必要がある
* テスト時には４つのアカウントを読み込んでいるため、この過程が必要

```
$ geth attach http://localhost:8545

Welcome to the Geth JavaScript console!

** 省略　**

> personal.newAccount("password")
```


## 2. コントラクトコードのコンパイル
* コントラクトコード（Solidityコード）自体は、好きなエディタで実装して良い。
* 出来上がったコントラクトコードを `contracts/` ディレクトリ以下に格納していく。
* コードのコンパイルは以下のコマンドを実行する。
* 実行結果（abi, bytecode, bytecode_runtime など）は `build/contracts.json` に保存される。

## 3. テスト
* テスト実行はpytestで実行する。
* テストコードを `tests/` の中に格納して、`tests`が存在するディレクトリで以下を実行する。

```
$ py.test tests/
```

* Warningの出力をさせたくない場合は、以下のオプションをつける。

```
$ py.test tests/ --disable-pytest-warnings
```
