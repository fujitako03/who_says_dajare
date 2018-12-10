from flask import Flask
from flask_bootstrap import Bootstrap
from controllers import dajare_page
import os
import sys

# 起動モード
args = sys.argv
mode = args[1] if (len(args) > 1 and args[1] == "futon") else "browser"
print(mode + " モードで起動")

# 環境変数に追加
os.environ['MODE'] = mode

# アプリケーションを作成
app = Flask(__name__)
bootstrap = Bootstrap(app)

# 分割先のコントローラー(Blueprint)を登録する
app.register_blueprint(dajare_page.app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)