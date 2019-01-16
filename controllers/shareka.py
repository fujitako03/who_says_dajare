import MeCab
import collections
from flask import Blueprint

# lueprintオブジェクトを生成します
app = Blueprint('dajarewake', __name__)


class Shareka:

    def __init__(self, sentence, n=2):
        """置き換える文字リストが格納されたクラス変数"""
        self.replace_words = [
            ["。", ""],
            ["、", ""],
            [",", ""],
            [".", ""],
            ["!", ""],
            ["！", ""],
            ["・", ""],
            ["「", ""],
            ["」", ""],
            ["「", ""],
            ["｣", ""],
            ["『", ""],
            ["』", ""],
            [" ", ""],
            ["　", ""],
            ["ッ", ""],
            ["ャ", "ヤ"],
            ["ュ", "ユ"],
            ["ョ", "ヨ"],
            ["ァ", "ア"],
            ["ィ", "イ"],
            ["ゥ", "ウ"],
            ["ェ", "エ"],
            ["ォ", "オ"],
            ["ー", ""]
        ]
        self.kaburi = n
        self.sentence = sentence

        mecab = MeCab.Tagger("-Oyomi")
        self.kana = mecab.parse(sentence)[:-1]
        self.preprocessed = self.preprocessing(self.kana)
        self.devided = self.devide(self.preprocessed)

    def preprocessing(self, sentence):
        for i, replace_word in enumerate(self.replace_words):
            sentence = sentence.replace(replace_word[0],replace_word[1])
        return sentence

    def devide(self, sentence):
        elements = []
        repeat_num = len(sentence) - (self.kaburi - 1)
        for i in range(repeat_num):
            elements.append(sentence[i:i+self.kaburi])
        return elements

    def list_max_dup(self):
        c = collections.Counter(self.devided)
        return c.most_common()[0] # (リストの再頻出の要素,出現数)

    def sentence_max_dup_rate(self, sentence):
        s = list(sentence)
        c = collections.Counter(s)
        return c.most_common()[0][1]/len(sentence)

    def dajarewake(self):
        if len(self.devided) == 0:
            return False
        elif self.list_max_dup()[1] > 1 and self.sentence_max_dup_rate(self.list_max_dup()[0]) <= 0.5:
            return True
        else:
            return False



if __name__ == '__main__':
    dj = Shareka("布団が吹っ飛んだ。」。。")
    print(dj.kana)
    print(dj.preprocessed)
    print(dj.dajarewake())
