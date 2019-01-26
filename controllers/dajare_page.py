from flask import render_template, Blueprint, request
from controllers.shareka import Shareka
from controllers.ukeruka import Ukeruka
from controllers.servo_moter import SG90
from datetime import datetime
from google.cloud import datastore
import pandas as pd
import numpy as np
import time
import os
import uuid

# lueprintオブジェクトを生成します
app = Blueprint('dajarepage', __name__)

# datastoreへ接続するためのクライエント
client = datastore.Client()

# 大喜利プレイヤーの並び順
authors = pd.read_csv("./data/authors.csv")
author_order = dict()
for index, row in authors.iterrows():
    author_order[row["author"]] = row["num"]

authors_list = authors.author

class DajarePage:
    @app.route('/', methods=['GET', 'POST'])
    def top():
        """
        トップページを表示
        :return:
        """
        if os.getenv("OGIRI") == "ogiri":
            return render_template("index_ogiri.html", authors_list=author_order)
        else:
            return render_template("index.html", author_order=authors_list)

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

    def dajare_insert_to_csv(self, dajare_text, dajare_author, dajare_score):
        # CSVに追記
        tdatetime = datetime.now()
        str_time = tdatetime.strftime('%Y-%m-%d %H:%M:%S')

        insert_df = pd.DataFrame([[str(uuid.uuid4()), str_time, dajare_text,dajare_author,dajare_score]])
        insert_df.to_csv("./data/ogiri_answer.csv", mode="a", header=False, index=False)

    def dajare_query_csv(self, filepath):
        # CSVに追記
        dajare_df = pd.read_csv(filepath)
        # 得点が高い順に並び替える
        sorted_df = dajare_df.sort_values('score', ascending=False)

        # 回答ごとに辞書のリスト化する
        dajare_list = []
        for index, row in sorted_df.iterrows():
            dajare_list.append(dict(row))

        return dajare_list

    def dajare_summary_csv(self, filepath, author_order, authors_list):
        # csvを読み込み
        dajare_df = pd.read_csv(filepath)

        # LEFT JOIN 用の空テーブル
        empty_df = pd.DataFrame({"author":authors_list})

        #回答者ごとに集計
        total_score = dajare_df.groupby("author", as_index=False )[["score"]].sum()
        # total_score["order_num"] = [author_order[a] for a in total_score.author]
        merged_score = pd.merge(empty_df, total_score, on="author", how="left")
        merged_score = merged_score.fillna(0)

        # 回答ごと
        score_list = []
        for index, row in merged_score.iterrows():
            score_list.append(dict(row))

        return score_list

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

            # 予測
            # 　デバッグモードの場合同じ点数をつける
            if os.getenv("DEBUG") == "debug":
                dajare_score = 66
            else:
                res = uk.predict(np.array([dajare]),
                                 model_filepath="./model/model.h5")
                dajare_score = round((res[0][0] - 0.56) * 10 * 100 + 55)

            # 100点を超えないように調整
            if dajare_score > 100:
                dajare_score = 99.99
            elif dajare_score < 0:
                dajare_score = 1

            # 結果によって布団をふっとばす
            if dajare_score > 50:
                wake_ans = "布団がふっとんだ！"
                futon_img = "futtonda.png"

                # モーターを動かす（futonモードの場合）
                if os.getenv('MODE') == "futon":
                    servo.setdirection(-50, 80)
                    time.sleep(0.7)
                    servo.cleanup()

            else:
                wake_ans = "吹っ飛ばない。。。（もっと面白いダジャレを言えるはず！）"
                futon_img = "futtobanai.png"

        else:
            wake_ans = "なんて？（ダジャレを入力してください）"
            futon_img = "nante.png"
            dajare_score = 0

        if os.getenv('OGIRI') == "ogiri":
            dj.dajare_insert_to_csv(dajare_text, dajare_author, dajare_score)
            dajare_list = dj.dajare_query_csv(filepath="./data/ogiri_answer.csv")
            total_score_list = dj.dajare_summary_csv(filepath="./data/ogiri_answer.csv",
                                                  author_order=author_order,
                                                     authors_list=authors_list)

            return render_template("dajaresult_ogiri.html",
                                   dajare_text=dajare_text,
                                   wake_ans=wake_ans,
                                   futon_img=futon_img,
                                   dajare_score=round(dajare_score, 2),
                                   dajare_list=dajare_list,
                                   total_score_list=total_score_list)
        else:
            # Datastoreへ保存・過去のデータを読み込み
            try:
                dj.dajare_insert_to_datastore(client, dajare_text, dajare_author, dajare_score)
                dajare_list = dj.dajare_query_datastore(client)
            except:
                dajare_list = None

        return render_template("dajaresult.html",
                               dajare_text=dajare_text,
                               wake_ans=wake_ans,
                               futon_img=futon_img,
                               dajare_score=round(dajare_score, 2),
                               dajare_list=dajare_list)


    # 結果のプレビュー画面
    @app.route('/preview', methods=['GET', 'POST'])
    def preview():
        """
        結果のプレビュー画面を表示
        :return:
        """
        dj = DajarePage()
        if os.getenv("OGIRI") == "ogiri":
            dajare_list = dj.dajare_query_csv(filepath="./data/ogiri_answer.csv")
            total_score_list = dj.dajare_summary_csv(filepath="./data/ogiri_answer.csv",
                                                     author_order=author_order,
                                                     authors_list=authors_list)
            return render_template("dajaresult_ogiri.html",
                                   dajare_list=dajare_list,
                                   total_score_list=total_score_list)
        else:
            # Datastoreへ保存・過去のデータを読み込み
            try:
                dajare_list = dj.dajare_query_datastore(client)
            except:
                dajare_list = None
            return render_template("dajaresult.html",
                                   dajare_list=dajare_list)