from flask import render_template, Blueprint, request
from controllers.dajare_wake import Dajarewake
from controllers.servo_moter import SG90
import time
import os

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

        # モーターを設定（futonモードの場合）
        if os.getenv('MODE') == "futon":
            servo = SG90(4, 50)

        # 判定結果により
        if is_dajare:
            wake_ans = "ふっとんだ！"

            # モーターを動かす（futonモードの場合）
            if os.getenv('MODE') == "futon":
                servo.setdirection(-50, 80)
                time.sleep(0.1)
                servo.cleanup()
        else:
            wake_ans = "なんて？"

        return render_template("dajaresult.html", dajare_text=dajare_text, wake_ans=wake_ans)