import MeCab
import collections
from flask import Blueprint

# lueprintオブジェクトを生成します
app = Blueprint('dajarewake', __name__)


class Dajarewake:
    """置き換える文字リストが格納されたクラス変数"""
    replace_words = [
    ["。、,.",""],
    ["ッ",""],
    ["ャ","ヤ"],
    ["ュ","ユ"],
    ["ョ","ヨ"],
    ["ァ","ア"],
    ["ィ","イ"],
    ["ゥ","ウ"],
    ["ェ","エ"],
    ["ォ","オ"],
    ["ー",""]
    ]
    def __init__(self, sentence, n = 3):
        self.kaburi = n
        self.sentence = sentence

        mecab = MeCab.Tagger("-Oyomi")
        self.kana = mecab.parse(sentence)[:-1]
        self.preprocessed = self.preprocessing(self.kana)
        self.devided = self.devide(self.preprocessed)

    def preprocessing(self, sentence):
        for i, replace_word in enumerate(self.replace_words):
            sentence = sentence.replace(replace_word[0], replace_word[1])
        return sentence

    def devide(self, sentence):
        elements = []
        repeat_num = len(sentence) - (self.kaburi - 1)
        for i in range(repeat_num):
            elements.append(sentence[i:i+self.kaburi])
        return elements

    def identity_num(self, element):
        char = []
        for i in range(len(element)):
            char.append(element[i])
        num = len(collections.Counter(char))
        return num

    def dajarewake(self):
        for i, element in enumerate(self.devided):
            for j in range(len(self.devided)):
                if i == j:
                    continue
                elif element == self.devided[j] and self.identity_num(element) != 1:
                    return True
                else:
                    continue
            return False


if __name__ == '__main__':
    dj = Dajarewake("布団が吹っ飛んだ")
    print(dj.dajarewake())
