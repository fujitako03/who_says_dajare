import os
import sys
import argparse
import logging

import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import Adam

from model import RNNModel
from datagenerator import Vocab, DataForGenerator
from tokenizer import TokenizerSpacy
from tensorflow.keras.optimizers import Adam

logging.basicConfig(level=logging.DEBUG)

def predict_dajare(args):
    dajare_raw = args.dajare
    weights_path = args.weights_path
    vocab_data_path = args.vocab_data_path

    tokenizer = TokenizerSpacy()

    dajare_words = tokenizer.tokenize_sentence(dajare_raw)
    logging.info(dajare_words)

    vocab = Vocab(vocab_data_path)
    dajare_labeled = vocab.convert_word2id(dajare_words)
    logging.info(dajare_labeled)

    batch_size = 30
    T = 25
    emb_size = 128
    hidden_size = 128
    dropout = 0.0
    lr = 1e-3
    vocab_size = vocab.vocab_num

    model = RNNModel(
        batch_size=batch_size,
        vocab_size=vocab_size,
        emb_size=emb_size,
        hidden_size=hidden_size,
        T=T,
        dropout=dropout,
        lr=lr,
        model_path=None)
    model.print_fn = logging.info

    model.load_weights(weights_path)

    probability = model.predict(model.predict(np.array([dajare_labeled], dtype=np.float32)))
    logging.info('Probability:',probability[0])
    return probability

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('dajare', help='')
    parser.add_argument('--weights_path', help='', required=False, default='./results/test_data/test.hdf5')
    parser.add_argument('--vocab_data_path', help='', required=False, default='../../data/test_data/sentence_data.txt')

    args = parser.parse_args()

    predict_dajare(args)