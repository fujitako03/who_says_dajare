import os,sys
import numpy as np

sys.path.append('../../notebook/scripts/modules/')
from datagenerator import Vocab

input_data_path = './results/test_data.csv'
output_data_path = './results/dummy_data.csv'

vocab = Vocab(input_data_path)
vocab_size = vocab.vocab_num
sentence_num = vocab.sentence_num
vocab_num = vocab.vocab_num

words = list(vocab.id2word.values())
n_words = [len(s) for s in vocab.sentences]

output_file = open(output_data_path, mode='w', encoding='utf-8')
for i, n_words in enumerate(n_words):
    dummy_sentence = np.random.choice(words, size=n_words, replace=False)
    dummy_sentence = [w for w in dummy_sentence]
    output_file.write(','.join(dummy_sentence)+'\n')

output_file.close()
