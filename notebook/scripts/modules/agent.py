import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Embedding, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.utils import to_categorical
import tensorflow as tf


class Agent(object):
    def __init__(self, sess, vocab_size, emb_size, hidden_size,
                 T, lr):
        self.sess = sess
        self.size = 1
        self.vocab_size = vocab_size
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.lr = lr
        self.T = T  # sentence_size

        self.pre_generator = self._build_pre_generator(
            vocab_size,
            emb_size,
            hidden_size
        )
        self.generator = Actor(
            sess,
            self.size,
            vocab_size,
            emb_size,
            hidden_size,
            T,
            lr
        )
        self.rollouter = Actor(
            sess,
            self.size,
            vocab_size,
            emb_size,
            hidden_size,
            T,
            lr
        )

    def _build_pre_generator(self, vocab_size, emb_size, hidden_size):
        data_inp = Input(shape=(None, ), dtype='int32', name='input')
        out = Embedding(
            vocab_size, emb_size, mask_zero=False, name='embedding'
        )(data_inp)
        out = LSTM(hidden_size, return_sequences=True, name='LSTM')(out)
        out = TimeDistributed(
            Dense(vocab_size, activation='softmax', name='dense_softmax'),
            name='time_dense_softmax')(out)
        pre_generator = Model(data_inp, out)
        return pre_generator

    def pre_train(self, g_data, g_pre_episodes, weight_path, g_pre_lr):
        g_optimizer = Adam(g_pre_lr)
        self.pre_generator.compile(g_optimizer, 'categorical_crossentropy')
        self.pre_generator.summary()
        self.pre_hist = self.pre_generator.fit_generator(
            g_data,
            steps_per_epoch=None,
            epochs=g_pre_episodes
        )
        self.pre_generator.save_weights(weight_path)
        self.inherit_weights(self.pre_generator, self.generator)
        self.inherit_weights(self.pre_generator, self.rollouter)

    def sample_words(self, prob):
        action = np.zeros((self.size, ), dtype=np.int32)
        for i in range(self.size):
            p = prob[i]
            action[i] = np.random.choice(self.vocab_size, p=p)
        return action

    def sample_sentences(self, actor, T, BOS=1):
        actor.reset_rnn_state()
        action = np.zeros([self.size, 1], dtype=np.int32)
        action[:, 0] = BOS
        actions = action
        for _ in range(T):
            prob, _, _ = actor.predict(action)
            action = self.sample_words(prob).reshape(-1, 1)
            actions = np.concatenate([actions, action], axis=-1)
        actions = actions[:, 1:]
        actor.reset_rnn_state()
        return actions

    def generate_id_samples(self, actor, T, sample_num, output_file):
        sentences_ids = []
        for _ in range(sample_num):
            actions = self.sample_sentences(actor, T)
            actions_list = actions.tolist()
            for ids in actions_list:
                ids_str = [str(id) for id in ids]
                sentences_ids.append(ids_str)
        output_str = ''
        for i in range(sample_num):
            output_str += ' '.join(sentences_ids[i]) + '\n'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_str)

    def get_action(self, state):
        s_t = state[:, -1:].reshape([-1, 1])
        prob, h, c = self.generator.predict(s_t)
        action_t = self.sample_words(prob).reshape([1, 1])
        is_end = self.projection(state)
        return action_t * is_end, h, c

    def rollout_sampling(self, action, epsilon=0.0):
        prob, h, c = self.rollouter.predict(action)
        action_t = self.sample_words(prob).reshape([1, 1])
        is_end = self.projection(action)
        return action_t * is_end

    def projection(self, state, PAD=0, EOS=2):
        is_PAD = state[:, -1:] == PAD
        is_EOS = state[:, -1:] == EOS
        is_END = 1 - is_PAD.astype(np.int) - is_EOS.astype(np.int)
        return is_END.reshape([1, 1])

    def rollout(self, step, state, action):
        Y_i = state[:, 1:]
        Y_i = np.concatenate([Y_i, action], axis=-1)
        for _ in range(self.T - 1 - step):
            _action = self.rollout_sampling(action)
            Y_i = np.concatenate([Y_i, _action], axis=-1)
            action = _action
        return Y_i

    def inherit_weights(self, agent, to_agent):
        i = 0
        for layer in agent.layers:
            if len(layer.get_weights()) != 0:
                w = layer.get_weights()
                to_agent.layers[i].set_weights(w)
                i += 1

    def initialize(self, g_pre_weight):
        self.pre_generator.load_weights(g_pre_weight)
        self.inherit_weights(self.pre_generator, self.generator)
        self.inherit_weights(self.pre_generator, self.rollouter)

    def reset_rnn_states(self):
        self.generator.reset_rnn_state()
        self.rollouter.reset_rnn_state()


class Actor(object):
    def __init__(self, sess, size, vocab_size, emb_size, hidden_size,
                 T, lr):
        self.sess = sess
        self.size = size
        self.vocab_size = vocab_size
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.T = T
        self.lr = lr
        self._build_graph()
        self.reset_rnn_state()

    def _build_graph(self):
        state_in = tf.placeholder(tf.float32, shape=(None, 1))
        h_in = tf.placeholder(tf.float32, shape=(None, self.hidden_size))
        c_in = tf.placeholder(tf.float32, shape=(None, self.hidden_size))
        action = tf.placeholder(tf.float32, shape=(None, self.vocab_size))
        reward = tf.placeholder(tf.float32, shape=(None, 1))

        self.layers = []

        embedding = Embedding(
            self.vocab_size, self.emb_size, mask_zero=False, name='embedding'
        )
        out = embedding(state_in)
        self.layers.append(embedding)

        lstm = LSTM(
            self.hidden_size, return_state=True, name='LSTM'
        )
        out, next_h, next_c = lstm(out, initial_state=[h_in, c_in])
        self.layers.append(lstm)

        dense = Dense(
            self.vocab_size, activation='softmax', name='densesoftmax'
        )
        prob = dense(out)
        self.layers.append(dense)

        log_prob = tf.log(tf.reduce_sum(prob * action, axis=-1))
        loss = - log_prob * reward
        optimizer = tf.train.AdamOptimizer(learning_rate=self.lr)
        minimize = optimizer.minimize(loss)

        self.state_in = state_in
        self.h_in = h_in
        self.c_in = c_in
        self.action = action
        self.reward = reward
        self.prob = prob
        self.next_h = next_h
        self.next_c = next_c
        self.minimize = minimize
        self.loss = loss

        self.init_op = tf.global_variables_initializer()
        self.sess.run(self.init_op)

    def reset_rnn_state(self):
        self.h = np.zeros([self.size, self.hidden_size])
        self.c = np.zeros([self.size, self.hidden_size])

    def set_rnn_state(self, h, c):
        self.h = h
        self.c = c

    def get_rnn_state(self):
        return self.h, self.c

    def predict(self, state, stateful=True):
        h = self.h
        c = self.c
        feed_dict = {
            self.state_in: state,
            self.h_in: h,
            self.c_in: c
        }
        prob, next_h, next_c = self.sess.run(
            [self.prob, self.next_h, self.next_c],
            feed_dict
        )

        self.h = next_h
        self.c = next_c
        return prob, next_h, next_c

    def update(self, state, action, reward, h=None, c=None, stateful=True):
        if h is None:
            h = self.h
        if c is None:
            c = self.c
        state = state.reshape(-1, 1)
        action = action.reshape(-1, 1)
        reward = reward.reshape(-1, 1)
        feed_dict = {
            self.state_in: state,
            self.h_in: h,
            self.c_in: c,
            self.action: to_categorical(action, self.vocab_size),
            self.reward: reward
        }
        _, loss, next_h, next_c = self.sess.run(
            [self.minimize, self.loss, self.next_h, self.next_c],
            feed_dict
        )

        if stateful:
            self.h = next_h
            self.c = next_c
            return loss
        else:
            return loss, next_h, next_c
