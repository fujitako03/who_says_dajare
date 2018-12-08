from flask import render_template, Blueprint, request
from controllers.dajare_wake import Dajarewake

# lueprintオブジェクトを生成します
app = Blueprint('dajarepage', __name__)


class DajarePage:
    @app.route('/', methods=['GET', 'POST'])
    def top():
        """
        トップページを表示
        :return:
        """
        return render_template("index.html")


    @app.route('/dajare_post', methods=['POST'])
    def dajare_post():
        """
        入力されたダジャレを判定し、結果ページを表示
        :return:
        """
        # フォームからダジャレを取得
        dajare_text = request.form.get('dajare_text')

        # ダジャレ判定
        dj = Dajarewake(dajare_text)
        is_dajare = dj.dajarewake()
        wake_ans = "だじゃれじゃ" if is_dajare else "だじゃれじゃない"

        return render_template("dajaresult.html", dajare_text=dajare_text, wake_ans=wake_ans)