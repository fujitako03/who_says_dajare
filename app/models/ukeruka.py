import numpy as np

class Ukeruka:
    def __init__(self, sentence):
        self.sentence = sentence
        self.result = None

    def evaluate(self):
        result = np.random.rand()
        self.result = result

    def to_dict(self):
        data = {
            'sentence': self.sentence,
            'result': self.result
        }
        return data
