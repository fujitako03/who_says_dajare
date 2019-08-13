import os

import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import Adam

from model import RNNModel
from datagenerator import Vocab, DataForGenerator

train_data_path = os.path.join('../../data/test_data/', 'sentence_data.txt')
id_train_data_path = os.path.join('../../data/test_data/', 'id_input.txt')
input_label = os.path.join('../../data/test_data/sentence_label.txt')
model_path = './results/test_data/test.hdf5'

vocab = Vocab(input_data)

vocab.write_word2id(input_data, id_input_data)

batch_size = 30
T = 25  # max_length of sentences
emb_size = ''

datagen = DataForGenerator(id_input_data, input_label, batch_size, T)

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
    model_path=model_path)
model.build_model(optimizer=Adam(lr), loss='binary_crossentropy', metrics=None)

steps_per_epoch = len(datagen)
epochs = 2

model.fit_generator(datagen.generate_training_data(), epochs, steps_per_epoch, validation_data=None)