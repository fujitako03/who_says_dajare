from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dropout, Dense, Embedding, LSTM
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

class RNNModel(object):
    def __init__(self, batch_size, vocab_size, emb_size, hidden_size, T, dropout, lr, model_path):
        self.vocab_size = vocab_size
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.T = T
        self.batch_size = batch_size
        self.dropout = dropout
        self.lr = lr
        self.model_path = model_path
        self._model = None

    def _construct_model(self):
        data_inp = Input(shape=(None, ), dtype='int32', name='input')
        out = Embedding(
            self.vocab_size, self.emb_size, mask_zero=False, name='embedding'
        )(data_inp)
        out = LSTM(self.hidden_size)(out)
        out = Dropout(self.dropout, name='dropout')(out)
        out = Dense(1, activation='sigmoid', name='dense_sigmoid')(out)
        return Model(data_inp, out)

    def _build_callbacks(self):
        model_checkpoint = ModelCheckpoint(self.model_path, save_best_only=True)
        tensorboard_checkpoint = TensorBoard(log_dir=self.model_path, write_graph=True)
        return [model_checkpoint, tensorboard_checkpoint]

    def build_model(self, optimizers, loss, metrics):
        self._model = self._construct_model()
        self._model.compile(optimizers=optimizers, loss=loss, metrics=metrics)

    def fit(self, x_train, y_train, epochs, steps_per_epoch, val_x, val_y):
        callbacks = self._build_callbacks()
        self._model.fit(
            x_train, y_train,
            batch_size=self.batch_size,
            epochs=epochs, steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
            validation_data=(val_x, val_y)
            )
        return 0

    def fit_generator(self, x_train_gen, y_train_gen, epochs, steps_per_epoch, val_x, val_y):
        callbacks = self._build_callbacks()
        self._model.fit_generator(
            x_train_gen, y_train_gen,
            batch_size=self.batch_size,
            epochs=epochs, steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
            validation_data=(val_x, val_y)
            )
        return 0