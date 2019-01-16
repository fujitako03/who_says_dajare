# #coding: utf-8
import numpy as np
import keras
from keras.optimizers import *
from keras.layers import *
from keras.callbacks import *
from keras.models import *
import MeCab
import re
from numpy import *
import codecs


class Ukeruka:

    def predict(self, comments, model_filepath="model.h5"):
        model = load_model(model_filepath)
        ret = model.predict(comments)
        return ret


    def share_to_yomi(self, raw_text):
        clean_text = re.sub('[『』、。！!（.*）「」?？ \n]', '', raw_text)
        clean_text = re.sub('〜', 'ー', clean_text)
        mecab = MeCab.Tagger("-Oyomi")
        kana = mecab.parse(clean_text)[:-1]

        if re.search("[a-zA-Z0-9]", kana):
            return np.nan
        else:
            return kana
