## summary

これから作るよ

# set up

以下のコマンドが利用出来る状態にする

```
$ python -V # python2系が使える（GCPのSDKを動すのはpython2系）
$ python3 -V # python3系が使える（アプリ起動はpython3系）
$ pip3 -V # python3系のパッケージ管理ができる
$ gcloud config list # GCPのSDKが使える 
$ npm -V # npmが使える
```

python3のパッケージをインストール

```
$ cd app
$ pip3 install -r requirements.txt
```

node.jsのパッケージをインストール

```
$ cd app/static
$ npm install 
```

# local test

2つ同時にサーバを起動する必要がある

APIサーバ起動

```
$ sh run_backend.sh
```

UIサーバ起動

```
$ sh run_frontend.sh
```

# deploy

初回のみ以下でデプロイ先を設定

```
$ gcloud init
```

以下でデプロイする

```
$ sh deploy.sh
```
