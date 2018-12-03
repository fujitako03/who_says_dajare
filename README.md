#ダジャレWEB API

## ダジャレチェック
### 処理概要
ダジャレかどうかの判定を返す

### Example
```
curl -X POST -d '{"text":"布団がふっとんだ"}' -H 'Content-Type:application/json;charset=UTF-8' https://who-says-dajare.appspot.com/isdajare
```

### Parameter
text: "ダジャレ本文"

### Response
ダジャレ：`{"is_dajare":"dajare"}`

ダジャレじゃない：`{"is_dajare":"dareja"}`

不正な入力`{"is_dajare":"unknown"}`
