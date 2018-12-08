from flask import Flask
from flask_bootstrap import Bootstrap
from controllers import top

# アプリケーションを作成
app = Flask(__name__)

# 分割先のコントローラー(Blueprint)を登録する
app.register_blueprint(top.app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)