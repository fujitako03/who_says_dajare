from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dropout, Dense, Embedding, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard


class Environment(object):
    def __init__(self, batch_size, vocab_size, emb_size, hidden_size,
                 T, dropout, lr):
        self.vocab_size = vocab_size
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.T = T
        self.batch_size = batch_size
        self.dropout = dropout
        self.lr = lr
        self.discriminator = self._build_graph(
            self.vocab_size,
            self.emb_size,
            self.hidden_size,
            self.dropout
        )

    def _build_graph(self, vocab_size, emb_size, hidden_size, dropout):
        data_inp = Input(shape=(None, ), dtype='int32', name='input')
        out = Embedding(
            vocab_size, emb_size, mask_zero=False, name='embedding'
        )(data_inp)
        out = LSTM(hidden_size)(out)
        out = Dropout(dropout, name='dropout')(out)
        out = Dense(1, activation='sigmoid', name='dense_sigmoid')(out)
        discriminator = Model(data_inp, out)
        return discriminator

    def pre_train(self, d_data, d_pre_episodes, d_pre_weight, d_pre_lr):
        d_optimizer = Adam(d_pre_lr)
        self.discriminator.compile(d_optimizer, 'binary_crossentropy')
        self.discriminator.summary()
        self.discriminator.fit_generator(
            d_data,
            steps_per_epoch=None,
            epochs=d_pre_episodes
        )
        self.discriminator.save_weights(d_pre_weight)

    def initialize(self, d_pre_weight):
        self.discriminator.load_weights(d_pre_weight)
        d_optimizer = Adam(self.lr)
        self.discriminator.compile(d_optimizer, 'binary_crossentropy')
