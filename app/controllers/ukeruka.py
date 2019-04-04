# #coding: utf-8
from controllers.shareka import Shareka
import MeCab
import re
import pandas as pd
import numpy as np, random
from sklearn.ensemble import RandomForestClassifier
import codecs
import pickle
import collections
import itertools
from gensim.models import KeyedVectors
import pickle
# import keras
# from keras.optimizers import *
# from keras.layers import *
# from keras.callbacks import *
# from keras.models import *
# import tensorflow as tf
# graph = tf.get_default_graph()

from flask import Blueprint

# # lueprintオブジェクトを生成します
# app = Blueprint('dajarewake', __name__)

class Ukeruka:

    def share_to_yomi(self, raw_text):
        clean_text = re.sub('[『』、。！!（.*）「」?？ \n]', '', raw_text)
        clean_text = re.sub('〜', 'ー', clean_text)
        mecab = MeCab.Tagger("-Oyomi")
        kana = mecab.parse(clean_text)[:-1]

        if re.search("[a-zA-Z0-9]", kana):
            return np.nan
        else:
            return kana

    def word_tokenaize(self, text):
        node = tagger.parseToNode(text)
        result = []
        while node:
            hinshi = node.feature.split(",")[0]
            if hinshi == '名詞' or hinshi == '動詞' or hinshi == '形容詞':
                word = node.feature.split(",")[6]
                try:
                    word = w2v_model[word]
                    result.append(word)
                except KeyError:
                    word = []
            node = node.next
        return result

    # 各ベクトルの距離を計算、格納する
    def cos_sim_combi(self, vec_list):
        # コサイン類似度
        def cos_sim(v1, v2):
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        result = []
        combi_list = list(itertools.combinations(vec_list, 2))

        try:
            for combi in combi_list:
                distances = cos_sim(combi[0], combi[1])
                result.append(np.nanmax(distances))
        except:
            return None

        return result

    def sentence_length(self, dajare_text):
        sh = Shareka(dajare_text)
        return len(sh.kana)

    def duplicate(self, dajare_text):
        i = 2
        repeat_num = []
        sh = Shareka(dajare_text, i)
        repeat_num.append(sh.list_max_dup()[1])
        while sh.dajarewake():
            i += 1
            sh = Shareka(dajare_text, i)
            repeat_num.append(sh.list_max_dup()[1])
        return i - 1, max(repeat_num)

    def nega_posi(self, text, npjp_dic):
        tagger = MeCab.Tagger()

        kaisekiyou = text.split('¥n')
        string = ' '.join(kaisekiyou)
        mecab = tagger.parse(string)

        kaigyou = mecab.splitlines()
        kaigyou = kaigyou[0:len(kaigyou) - 1]

        for tango_list in kaigyou:
            tab = tango_list.split('\t')

        len_text = 0
        sum_score = 0
        scores = []
        for tango_list in kaigyou:
            tab = tango_list.split('\t')[1].split(",")[6]
            hinshi = tango_list.split('\t')[1].split(",")[0]
            if hinshi in ["名詞", "形容詞", "動詞"]:
                if tab in npjp_dic:
                    pn_score = npjp_dic[tab]  # 辞書から対応する単語の点数を抽出
                    # len_text = len_text + 1
                else:
                    pn_score = np.random.normal(-0.3197, 0.1)  # 乱数で埋める

                len_text = len_text + 1
                sum_score = sum_score + pn_score
                scores.append(pn_score)
            else:
                continue
        return sum_score / len_text, max(scores), min(scores)

    def create_features(self, dajare_text, npjp_dic):
        sh = Shareka(dajare_text)
        uk = Ukeruka()
        dajare_preprocessed = sh.preprocessed

        sentence_length = len(sh.kana)  # ダジャレの文字数
        duplicate_num = uk.duplicate(dajare_text)[0]  # 重なり文字数
        repeat_num = uk.duplicate(dajare_text)[1]  # 重複繰り返し数
        dajarate = duplicate_num * repeat_num / sentence_length  # だじゃRate

        # 極性
        negapoji = uk.nega_posi(dajare_text, npjp_dic)
        negapoji_ave = negapoji[0]  # 平均極性スコア
        negapoji_max_positive = negapoji[1]  # 最大のポジティブスコア
        negapoji_max_negative = negapoji[2]  # 最大のネガティブスコア

        # 類似度
        # distances = uk.cos_sim_combi(uk.word_tokenaize(dajare_text))
        # ave_similarity = np.mean(distances) if len(distances) > 0 else 0
        # max_similarity = max(distances) if len(distances) > 0 else 0
        # min_similarity = min(distances) if len(distances) > 0 else 0

        dajare_features = [sentence_length, duplicate_num, repeat_num, dajarate, negapoji_ave,
                           negapoji_max_positive, negapoji_max_negative]
                           # ave_similarity, max_similarity, min_similarity]
        return dajare_features

    def predict(self, x_test, model):
        result = model.predict([x_test])
        return result



if __name__ == '__main__':
    dj = Shareka("布団が吹っ飛んだ。」。。")
    print(dj.kana)
    print(dj.preprocessed)
    print(dj.dajarewake())


# character level cnn ===
# class Ukeruka:
#
#     def predict(self, comments, model_filepath="model.h5"):
#         global graph
#         with graph.as_default():
#             model = load_model(model_filepath)
#             ret = model.predict(comments)
#             return ret
#
#
#     def share_to_yomi(self, raw_text):
#         clean_text = re.sub('[『』、。！!（.*）「」?？ \n]', '', raw_text)
#         clean_text = re.sub('〜', 'ー', clean_text)
#         mecab = MeCab.Tagger("-Oyomi")
#         kana = mecab.parse(clean_text)[:-1]
#
#         if re.search("[a-zA-Z0-9]", kana):
#             return np.nan
#         else:
#             return kana
