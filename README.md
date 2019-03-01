## summary
これから作るよ

# deploy

イメージファイル作成
```
$ sh build.sh
```

コンソール起動
```
$ sh run.sh
```

GCP SDK初期化
```
$ gcloud init
```

デプロイ
```
$ gcloud app deploy 
```

# local test

API起動
```
$ cd app/
$ python3 main.py
```

UI初期化、起動
```
$ cd app/static
$ npm install 
$ npm start
```

# reference
tkazusa/docker-appengine-python37
https://github.com/tkazusa/docker-appengine-python37
