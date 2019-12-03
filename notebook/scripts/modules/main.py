import os
import sys 
import glob
import argparse
from datetime import datetime
import logging

import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import Adam

from model import RNNModel
from datagenerator import Vocab, DataForGenerator

def display_params(logger, params):
    logger.info("# Hyper Parameters")
    for name, value in params.items():
        logger.info(name + ":{}".format(value))

def train(args):
    positive_data_dir = args.positive_data_dir
    negative_data_dir = args.negative_data_dir

    emb_size = args.emb_size
    hidden_size = args.hidden_size
    dropout = args.dropout
    lr = args.learning_rate

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = 'wiki_'+timestamp
    result_dir = os.path.join(args.result_dir, result_dir)
    if  not os.path.exists(result_dir):
        os.makedirs(result_dir)

     # Output to Stream
    handler1 = logging.StreamHandler()
    handler1.setLevel(logging.DEBUG)
    handler1.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))

    # Output to log file
    handler2 = logging.FileHandler(filename=os.path.join(result_dir, "log_{}.log".format(timestamp)))
    handler2.setLevel(logging.DEBUG)
    handler2.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))

    logger = logging.getLogger("StyleLearning.wiki")
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    logger.info("results data will be saved at {}".format(result_dir))

    positive_data_path = [p for p in glob.glob(os.path.join(positive_data_dir, "**/*"), recursive=True) 
                            if os.path.isfile(p)]
    negative_data_path = [p for p in glob.glob(os.path.join(negative_data_dir, "**/*"), recursive=True)
                            if os.path.isfile(p)]

    positive_data_path.sort()
    negative_data_path.sort()

    epochs = args.epochs

    positive_data_path = positive_data_path[:300]
    negative_data_path = negative_data_path[:300]

    batch_size = 32
    T = 32

    data_gen = DataForGenerator(batch_size=batch_size, T=T)

    for d in positive_data_path:
        data_gen.load_sentenceid_data(d, label=True)

    for d in negative_data_path:
        data_gen.load_sentenceid_data(d, label=False)

    logger.info("Building vocablary...")
    data_gen.load_vocab('./vocab.csv', vocab_size=50000)
    data_gen.make_train_and_test_data()
    test_data = data_gen.get_test_data()

    vocab_size = len(data_gen.vocab.word2id)
    logger.info("Vocab size: ", vocab_size)

    gen = data_gen.generate_training_data()

    model = RNNModel(
        batch_size=batch_size,
        vocab_size=vocab_size,
        emb_size=emb_size,
        hidden_size=hidden_size,
        T=T,
        dropout=dropout,
        lr=lr,
        model_path=result_dir)
    model.build_model(optimizer=Adam(lr), loss='binary_crossentropy', metrics=['accuracy'])

    steps_per_epoch = len(data_gen)

    display_params(logger, \
        {"batch_size": batch_size, "padding_size":T, "emb_size":emb_size, "hidden_size":128, "dropout":dropout, "learning_rate":lr})

    model.fit_generator(generator=gen, epochs=epochs, steps_per_epoch=steps_per_epoch, validation_data=test_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("positive_data_dir", help="", type=str)
    parser.add_argument("negative_data_dir", help='', type=str)
    parser.add_argument("--epochs", help='', type=int, default=2)
    parser.add_argument("--result_dir", help='', default='./results/', type=str)
    parser.add_argument("--emb_size", help="", type=int, default=128)
    parser.add_argument("--hidden_size", help="", type=int, default=128)
    parser.add_argument("--dropout", help="", type=float, default=0.5)
    parser.add_argument("--learning_rate", help="", type=float, default=0.01)

    args = parser.parse_args()

    train(args)