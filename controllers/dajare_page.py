from flask import render_template, Blueprint, request
from controllers.shareka import Shareka
from controllers.ukeruka import Ukeruka
from controllers.servo_moter import SG90
from datetime import datetime
from google.cloud import datastore
import numpy as np
import time
import os
import uuid

# lueprintオブジェクトを生成します
app = Blueprint('dajarepage', __name__)

# datastoreへ接続するためのクライエント
client = datastore.Client()


class DajarePage:
    @app.route('/', methods=['GET', 'POST'])
    def top():
        """
        トップページを表示
        :return:
        """
        return render_template("index.html")

    def dajare_insert_to_datastore(self, client, dajare_text, dajare_author, dajare_score):
        # DataStoreに格納
        tdatetime = datetime.now()
        str_time = tdatetime.strftime('%Y-%m-%d %H:%M:%S')

        key = client.key('Dajare')
        dajare_key = datastore.Entity(key)
        dajare_key.update({
            'dajare_id': str(uuid.uuid4()),
            'datetime': str_time,
            'dajare': dajare_text,
            'author': dajare_author,
            'score': dajare_score
        })
        client.put(dajare_key)

    def dajare_query_datastore(self, client):
        query = client.query(kind='Dajare')
        dajare_list = list(query.fetch())
        sorted_dajare = sorted(dajare_list, key=lambda dajare: dajare["score"], reverse=True)
        return sorted_dajare

    @app.route('/dajare_post', methods=['POST'])
    def dajare_post():
        """
        入力されたダジャレを判定し、結果ページを表示
        :return:
        """

        # フォームの情報を取得
        dajare_text = request.form.get('dajare_text')
        dajare_author = request.form.get('dajare_author')

        # ダジャレ判定
        sh = Shareka(dajare_text)
        is_dajare = sh.dajarewake()
        is_dajare = True

        # ダジャレ評価AI
        uk = Ukeruka()

        dj = DajarePage()

        # モーターを設定（futonモードの場合）
        if os.getenv('MODE') == "futon":
            servo = SG90(4, 50)

        # 判定結果により
        if is_dajare:

            # ダジャレ評価
            kana_dajare = uk.share_to_yomi(dajare_text)
            dajare = [ord(x) for x in kana_dajare]
            dajare = dajare[:30]
            if len(dajare) < 30:
                dajare += ([0] * (30 - len(dajare)))
            res = uk.predict(np.array([dajare]),
                             model_filepath="./model/model.h5")
            dajare_score = res[0][0] * 100

            # 結果によって布団をふっとばす
            if dajare_score > 50:
                wake_ans = "ふっとんだ！"

                # モーターを動かす（futonモードの場合）
                if os.getenv('MODE') == "futon":
                    servo.setdirection(-50, 80)
                    time.sleep(0.7)
                    servo.cleanup()
            else:
                wake_ans = "吹っ飛ばない。。。"

        else:
            wake_ans = "・・・・・・・・なんて？"
            dajare_score = 0

        # Datastoreへ保存・過去のデータを読み込み
        try:
            dj.dajare_insert_to_datastore(client, dajare_text, dajare_author, dajare_score)
            dajare_list = dj.dajare_query_datastore(client)
        except:
            dajare_list = None

        return render_template("dajaresult.html",
                               dajare_text=dajare_text,
                               wake_ans=wake_ans,
                               dajare_score=round(dajare_score, 2),
                               dajare_list=dajare_list)
