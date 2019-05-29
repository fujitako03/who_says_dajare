import numpy as np

from models import Shareka


class Ukeruka:
    def __init__(self, sentence):
        self.sentence = sentence
        self.result = None

        self.sentence_length = None
        self.duplicate_num = None
        self.repeat_num = None

        self.np_ave = None
        self.p_max = None
        self.n_max = None

    def evaluate(self):
        shareka = Shareka(self.sentence)
        shareka.divide()

        self.sentence_length = len(shareka.yomi)
        self.duplicate_num = 0
        self.repeat_num = 0
        for i in range(2, self.sentence_length):
            sh = Shareka(self.sentence, i)
            sh.divide()
            sh.evaluate()
            if sh.is_dajare:
                self.repeat_num = i
                self.duplicate_num = sh.max_dup
            else:
                break

        self.dajarate = \
            self.duplicate_num * self.repeat_num / self.sentence_length

        result = np.random.randint(low=1, high=100)
        self.result = result

    def to_dict(self):
        return {
            'sentence': self.sentence,
            'result': self.result,
            'sentence_length': self.sentence_length,
            'duplicate_num': self.duplicate_num,
            'repeat_num': self.repeat_num,
            'np_ave': self.np_ave,
            'p_max': self.p_max,
            'n_max': self.n_max,
            'dajarate': self.dajarate,
        }


if __name__ == '__main__':
    # dajare = '「布団が吹っ飛んだ。」'
    dajare = 'メンターランチで食べたラーメン'
    ukeruka = Ukeruka(dajare)
    ukeruka.evaluate()
    print(ukeruka.to_dict())
