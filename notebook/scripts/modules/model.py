import os
from tensorflow.keras.models import Model, load_model, Sequential
from tensorflow.keras.layers import Input, Dropout, Dense, Embedding, LSTM
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

class RNNModel(object):
    def __init__(self, batch_size, vocab_size, emb_size, hidden_size, T, dropout, lr, model_path, model_file_form="{epoch:02d}-{val_loss:.2f}.hdf5"):
        self.vocab_size = vocab_size
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.T = T
        self.batch_size = batch_size
        self.dropout = dropout
        self.lr = lr
        self.model_path = model_path
        self._model = None
        self.print_fn = None
        self.model_file_form = model_file_form

    def _construct_model(self):
        model = Sequential()
        model.add(Embedding(self.vocab_size, self.emb_size, name='embedding', mask_zero=True, trainable=True, input_length=self.T))
        model.add(LSTM(self.hidden_size, return_sequences=False))
        model.add(Dense(self.hidden_size, activation='relu', name='hidden'))
        model.add(Dropout(self.dropout, name='dropout'))
        model.add(Dense(1, activation='sigmoid', name='dense_sigmoid'))
        return model

    def _build_callbacks(self):
        model_checkpoint = ModelCheckpoint(os.path.join(self.model_path, self.model_file_form), save_best_only=True)
        tensorboard_checkpoint = TensorBoard(log_dir=self.model_path, write_graph=True)
        return [model_checkpoint, tensorboard_checkpoint]

    def build_model(self, optimizer, loss, metrics):
        self._model = self._construct_model()
        self._model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        self._model.summary(print_fn=self.print_fn)

    def fit(self, x_train, y_train, epochs, steps_per_epoch, val_x, val_y):
        callbacks = self._build_callbacks()
        self._model.fit(
            x_train, y_train,
            batch_size=self.batch_size,
            epochs=epochs, steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
            validation_data=None
            )
        return 0

    def fit_generator(self, generator, epochs, steps_per_epoch, validation_data):
        callbacks = self._build_callbacks()
        self._model.fit_generator(
            generator,
            epochs=epochs, steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
            validation_data=validation_data
            )
        return 0
    
    def load_weights(self, weights_path):
        self._model = load_model(weights_path)
        self._model.summary(print_fn=self.print_fn)
        
    def predict(self, sentence):
        prob = self._model.predict(sentence)
        return prob