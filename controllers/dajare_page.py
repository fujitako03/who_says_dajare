from flask import render_template, Blueprint, request
from controllers.shareka import Shareka
from controllers.ukeruka import Ukeruka
from controllers.servo_moter import SG90
from datetime import datetime
from google.cloud import datastore
from gensim.models import KeyedVectors
from joblib import dump, load
import pickle
import pandas as pd
import numpy as np
from numpy.random import normal
import time
import os
import uuid
import random

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

# 保存したモデルをロードする
r_model_path = './model/rf_classifier_raspberry.joblib'
rf_model = load(r_model_path)

# # read w2v model
# model_dir = './model/entity_vector.model.bin'
# w2v_model = KeyedVectors.load_word2vec_format(model_dir, binary=True)

# read negapoji_dix
np_df = pd.read_csv("./data/np_ja.dic", sep=':', header=None)
np_df.columns = ["word", "kana", "part", "np_score"]
np_df.head(2)
npjp_dic = dict()
for index, row in np_df.iterrows():
    npjp_dic[row.word] = row.np_score

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
            # ヒント単語¥
            tango_normal = pd.read_csv("./data/tango_normal.csv")
            tango_ryukogo = pd.read_csv("./data/tango_ryukogo.csv")
            normal_tango_list = random.sample(list(tango_normal.word), 10)
            ryuko_tango_list = random.sample(list(tango_ryukogo.word), 10)
            return render_template("index.html", author_order=authors_list,
                                   normal_tango_list=normal_tango_list,
                                   ryuko_tango_list=ryuko_tango_list)

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
        checkbox_values = request.form.getlist('dajare_label')
        translate_flg = 1 if "1" in checkbox_values else 0
        reration_flg = 1 if "2" in checkbox_values else 0
        potential_flg = 1 if "3" in checkbox_values else 0

        # ダジャレ判定
        sh = Shareka(dajare_text)
        is_dajare = sh.dajarewake()

        # ダジャレ評価AI
        uk = Ukeruka()

        dj = DajarePage()

        # モーターを設定（futonモードの場合）
        if os.getenv('MODE') == "futon":
            pass
            # servo = SG90(4, 50)

        # 判定結果により
        if is_dajare or (len(checkbox_values) > 0):

            # 予測
            # 　デバッグモードの場合同じ点数をつける
            if os.getenv("DEBUG") == "debug":
                dajare_score = 66
            elif dajare_text in ["布団がふっとんだ", "ふとんがふっとんだ"]:
                dajare_score = 210
            else:
                # ダジャレ評価
                features = uk.create_features(dajare_text, npjp_dic)
                features.extend([translate_flg, reration_flg, potential_flg])
                print(features)
                pred_prob = rf_model.predict_proba([features])
                pred_prob = pred_prob + normal(0.03, 0.05)
                dajare_score = round(pred_prob[0][1] * 100)
                dajare_score = 100 if dajare_score > 100 else dajare_score

            # 結果によって布団をふっとばす
            if dajare_score > 80:
                wake_ans = "布団がふっとんだ！"
                futon_img = "futtonda.png"

                # モーターを動かす（futonモードの場合）
                if os.getenv('MODE') == "futon":
                    servo = SG90(4, 50)
                    servo.setdirection(-50, 80)
                    time.sleep(0.7)
                    # モーターをクリーンアップ
                    servo.cleanup()


            else:
                wake_ans = "吹っ飛ばない。。。"
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
                                   dajare_score=int(dajare_score),
                                   dajare_list=dajare_list,
                                   total_score_list=total_score_list)
        else:
            # Datastoreへ保存・過去のデータを読み込み
            try:
                if not dajare_text in ["布団がふっとんだ", "ふとんがふっとんだ"]:
                    dj.dajare_insert_to_datastore(client, dajare_text, dajare_author, dajare_score)
                dajare_list = dj.dajare_query_datastore(client)
            except:
                dajare_list = None

        return render_template("dajaresult.html",
                               dajare_text=dajare_text,
                               wake_ans=wake_ans,
                               futon_img=futon_img,
                               dajare_score=int(dajare_score),
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