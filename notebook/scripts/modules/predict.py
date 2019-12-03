import os
import sys 
import glob
import argparse
from datetime import datetime

import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import Adam
import spacy

from model import RNNModel
from datagenerator import Vocab, DataForGenerator

def train(args):
    checkpoint_path = args.checkpoint_path
    dajare_sentence = args.query

    nlp = spacy.load('ja_ginza_nopn')

    words = nlp(dajare_sentence)
    words = [w.orth_ for w in words]

    batch_size = 32
    T = 32
    emb_size = 128
    hidden_size = 128
    dropout = 0.0
    lr = 1e-3

    data_gen = DataForGenerator(batch_size=batch_size, T=T)
    data_gen.load_vocab('./vocab.csv', vocab_size=50000)

    words_id, _ = data_gen.preprocess([words], None)

    vocab_size = len(data_gen.vocab.word2id)
    print("Vocab size: ", vocab_size)

    model = RNNModel(
        batch_size=batch_size,
        vocab_size=vocab_size,
        emb_size=emb_size,
        hidden_size=hidden_size,
        T=T,
        dropout=dropout,
        lr=lr,
        model_path=None)

    model.load_weights(checkpoint_path)

    print(words)
    print(words_id)

    pred = model.predict(words_id[0])

    print(pred)
    print(pred.shape)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint_path", help='', type=str)
    parser.add_argument("query", help="", type=str)
    args = parser.parse_args()

    train(args)