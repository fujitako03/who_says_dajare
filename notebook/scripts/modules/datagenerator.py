import linecache
import random

import numpy as np
import pandas as pd
from tensorflow.keras.utils import Sequence
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split


class Vocab(object):
    def __init__(self, sentences_path=None, delimiter=' '):
        self.PAD = 0
        self.BOS = 1
        self.EOS = 2
        self.UNK = 3
        self.PAD_TOKEN = '<PAD>'
        self.BOS_TOKEN = '<S>'
        self.EOS_TOKEN = '</S>'
        self.UNK_TOKEN = '<UNK>'
        self.word2id = {
            self.PAD_TOKEN: self.PAD,
            self.BOS_TOKEN: self.BOS,
            self.EOS_TOKEN: self.EOS,
            self.UNK_TOKEN: self.UNK,
        }
        self.id2word = {v: k for k, v in self.word2id.items()}
        self.word_counter = {}

        if sentences_path is not None:
            self.sentences = self.load_data(sentences_path)
            self.build_vocab(self.sentences)
            self.vocab_num = len(self.word2id)
            self.sentence_num = len(self.sentences)

    def update_vocab(self, sentences, min_count=1):
        
        for sentence in sentences:
            for word in sentence:
                self.word_counter[word] = self.word_counter.get(word, 0) + 1
        for word, count in sorted(
            self.word_counter.items(), key=lambda x: x[1], reverse=True
        ):
            if count < min_count:
                break
            _id = len(self.word2id)
            self.word2id.setdefault(word, _id)
            self.id2word[_id] = word

    def build_vocab(self, sentences, min_count=1):
        word_counter = {}
        for sentence in sentences:
            for word in sentence:
                word_counter[word] = word_counter.get(word, 0) + 1
        for word, count in sorted(
            word_counter.items(), key=lambda x: x[1], reverse=True
        ):
            if count < min_count:
                break
            _id = len(self.word2id)
            self.word2id.setdefault(word, _id)
            self.id2word[_id] = word

    def write_word2id(self, sentences_path, output_path):
        ids_sentences = []
        for line in open(sentences_path, encoding='utf-8'):
            words = line.strip().split()
            ids_words = [
                str(self.word2id.get(word, self.UNK)) for word in words
            ]
            ids_sentences.append(ids_words)
        self.data_num = len(ids_sentences)
        output_str = ''
        for i in range(count_data(sentences_path)):
            output_str += ' '.join(ids_sentences[i]) + '\n'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_str)

    def write_id2word(self, ids_path, output_path):
        sentences = []
        for line in open(ids_path, 'r', encoding='utf-8'):
            ids = line.strip().split()
            words_ids = [
                self.id2word.get(int(id), self.UNK_TOKEN) for id in ids
            ]
            sentences.append(words_ids)
        output_str = ''
        for i in range(count_data(ids_path)):
            output_str += ' '.join(sentences[i]) + '\n'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_str)

    def convert_word2id(self, tokenized_sentence):
        sentence_labeled = [self.word2id.get(word, self.UNK) for word in tokenized_sentence]
        return sentence_labeled

    def load_data(file_path, split=' '):
        data = []
        for line in open(file_path, encoding='utf-8'):
            words = line.strip().split(split)
            data.append(words)
        return data

    def count_data(self, file_path):
        return len(open(file_path, encoding='utf-8'))

    def sentence_to_ids(self, sentence):
        ids = [self.word2id.get(word, self.UNK) for word in sentence]
        return ids

    def load_vocab(self, vocab_path, vocab_size):
        vocab_df = pd.read_csv(vocab_path, header=None)
        self.word2id = dict([(k,ids) for k, ids in zip(vocab_df.loc[:vocab_size, 0], vocab_df.loc[:vocab_size, 1])])

class DataForGenerator(Sequence):
    def __init__(self, batch_size, T, shuffle=True, bos=1, eos=2):

        self.positive_sentence_data = []
        self.negative_sentence_data = []
 
        self.batch_size = batch_size
        self.T = T
        self.shuffle = shuffle
        self.BOS = bos
        self.EOS = eos

        self.n_data = 0

        self.vocab = Vocab()

        self.reset()

    def __len__(self):
        return self.n_data // self.batch_size

    def load_sentenceid_data(self, ids_path, label=True):

        with open(ids_path, encoding='utf-8') as f:
            for i, l in enumerate(f.readlines()):
                l = l.split()
                if label == True:
                    if len(l) >= 3:
                        self.positive_sentence_data.append(l)
                else:
                    self.negative_sentence_data.append(l)

        self.n_data = len(self.positive_sentence_data) +  len(self.negative_sentence_data)

    def load_vocab(self, vocab_path,vocab_size):
        self.vocab.load_vocab(vocab_path, vocab_size)

    def build_vocab(self):
        self.vocab.build_vocab(self.positive_sentence_data + self.negative_sentence_data)

    def generate_training_data(self):
        n_positive_data = len(self.positive_train_data)
        n_negative_data = len(self.negative_train_data)
        assert n_positive_data!=0 and n_negative_data!=0
        idx = 0 
        size_positive_batch = self.batch_size // 2
        size_negative_batch = self.batch_size - size_positive_batch

        def reset():
            positive_indices = np.arange(n_positive_data - (n_positive_data%size_positive_batch))
            negative_indices = np.arange(n_negative_data - (n_negative_data%size_negative_batch))
            random.shuffle(positive_indices)
            random.shuffle(negative_indices)
            positive_indices = np.reshape(positive_indices, (-1, size_positive_batch))
            negative_indices = np.reshape(negative_indices, (-1, size_negative_batch))
            return positive_indices, negative_indices

        while True:

            positive_indices, negative_indices = reset()
            for p_idx, n_idx in zip(positive_indices, negative_indices):
                positive_data = self.positive_train_data[p_idx]
                negative_data = self.negative_train_data[n_idx]

                batch_x = np.concatenate((positive_data, negative_data), axis=0)
                batch_y = [[1] for _ in range(size_positive_batch)] + [[0] for _ in range(size_negative_batch)]

                batch_x, batch_y = self.preprocess(batch_x, batch_y)
                idx += 1
                yield (np.array(batch_x), np.array(batch_y))


    def make_train_and_test_data(self):
        self.positive_train_data, self.positive_test_data = train_test_split(self.positive_sentence_data, test_size=0.1)
        self.negative_train_data, self.negative_test_data = train_test_split(self.negative_sentence_data, test_size=0.1)
        self.positive_train_data = np.array(self.positive_train_data)
        self.negative_train_data = np.array(self.negative_train_data)

    def get_test_data(self):
        positive_test_pad, positive_y = self.preprocess(self.positive_test_data, [[1] for _ in self.positive_test_data])
        negative_test_pad, negative_y = self.preprocess(self.negative_test_data, [[0] for _ in self.negative_test_data])
        test_x = positive_test_pad + negative_test_pad
        test_y = positive_y + negative_y
        n_test = len(test_x)
        n_test -= n_test % self.batch_size
        test_x = test_x[:n_test]
        test_y = test_y[:n_test]
        return (np.array(test_x), np.array(test_y))

    def preprocess(self, row_x, row_y):
        ids_x = list(map(self.vocab.sentence_to_ids, row_x))
        ids_x = list(map(self.padding, ids_x))
        return ids_x, row_y

    def reset(self):
        self.idx = 0
        if self.shuffle:
            self.shuffled_indices = np.arange(self.n_data)
            random.shuffle(self.shuffled_indices)

    def on_epoch_end(self):
        self.reset()

    def padding(self, sentences, PAD=0):
        sentences = [PAD for i in range(self.T - len(sentences))] + sentences
        if len(sentences) > self.T:
            sentences = sentences[-1 * self.T:]
        return sentences
