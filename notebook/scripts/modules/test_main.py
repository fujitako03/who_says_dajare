
import os

import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K

from agent import Agent
from datagenerator import Vocab, DataForGenerator, DataForDiscriminator
from environment import Environment



sess = tf.Session()
K.set_session(sess)

# hyperparameters
batch_size = 30
T = 25  # max_length of sentences
emb_size = 128  # embedding size
g_hidden = 128  # generator hidden size
d_hidden = 64  # discriminator hidden size
g_lr = 1e-3  # generator learning rate in the reinforcement learning
d_lr = 1e-3  # discrminator learning rate in the reinforcement learning
dropout = 0.0

# pretraining parameters
g_pre_lr = 1e-2  # generator pre_training learning rate
d_pre_lr = 1e-2  # discriminator pre_training learning rate
g_pre_episodes = 10  # generator pre_training epochs
d_pre_episodes = 4  # discriminator pre_training epochs
d_epochs = 1

# training parameters
adversarial_nums = 10
g_train_nums = 1  # number of generator train per adversarial learning
d_train_nums = 1  # number of discriminator train per adversarial learning
g_episodes = 50  # sentence num per generator update
n_sampling = 16  # number of monte calro tree
frequency = 1

# preprocess
input_data = os.path.join('data', 'input.txt')
id_input_data = os.path.join('data', 'id_input.txt')
pre_output_data = os.path.join('data', 'pre_generated_sentences.txt')
pre_id_output_data = os.path.join('data', 'pre_id_generated_sentences.txt')
output_data = os.path.join('data', 'generated_sentences.txt')
id_output_data = os.path.join('data', 'id_generated_sentences.txt')
os.makedirs('data/save', exist_ok=True)
g_pre_weight = os.path.join('data', 'save', 'pre_g_weights.h5')
d_pre_weight = os.path.join('data', 'save', 'pre_d_weights.h5')

vocab = Vocab(input_data)
vocab_size = vocab.vocab_num
pos_sentence_num = vocab.sentence_num
vocab.write_word2id(input_data, id_input_data)
sampling_num = vocab.data_num

env = Environment(batch_size, vocab_size, emb_size, d_hidden, T, dropout, d_lr)
agent = Agent(sess, vocab_size, emb_size, g_hidden, T, g_lr)


def pre_train():
    g_data = DataForGenerator(id_input_data, batch_size, T, vocab)
    agent.pre_train(g_data, g_pre_episodes, g_pre_weight, g_pre_lr)
    agent.generate_id_samples(
        agent.generator,
        T,
        sampling_num,
        pre_id_output_data
    )
    vocab.write_id2word(pre_id_output_data, pre_output_data)
    d_data = DataForDiscriminator(
        id_input_data,
        pre_id_output_data,
        batch_size,
        T,
        vocab
    )
    env.pre_train(d_data, d_pre_episodes, d_pre_weight, d_pre_lr)


def train():
    agent.initialize(g_pre_weight)
    env.initialize(d_pre_weight)
    for adversarial_num in range(adversarial_nums):
        print('---------------------------------------------')
        print('Adversarial Training: ', adversarial_num + 1)
        for _ in range(g_train_nums):
            g_train()
        print('Generator is trained')

        for _ in range(d_train_nums):
            d_train()
        print('Discriminator is trained')

        if adversarial_num % frequency == 0:
            sentences_history(
                adversarial_num,
                agent,
                T,
                vocab,
                sampling_num
            )


def g_train():
    batch_states = np.array([[]], dtype=np.int32)
    batch_actions = np.array([[]], dtype=np.int32)
    batch_rewards = np.array([[]], dtype=np.float32)
    batch_hs = np.array([[]], dtype=np.float32)
    batch_cs = np.array([[]], dtype=np.float32)
    for g_episode in range(g_episodes):
        agent.reset_rnn_states()
        states = np.zeros([1, 1], dtype=np.int32)
        states[:, 0] = vocab.BOS
        actions = np.array([[]], dtype=np.int32)
        rewards = np.array([[]], dtype=np.float32)
        hs = np.zeros([1, g_hidden], dtype=np.float32)
        cs = np.zeros([1, g_hidden], dtype=np.float32)
        for step in range(T):
            action, next_h, next_c = agent.get_action(states)
            agent.rollouter.reset_rnn_state()
            reward = mc_search(step, states, action, next_h, next_c)
            states = np.concatenate([states, action], axis=-1)
            rewards = np.concatenate([rewards, reward], axis=-1)
            actions = np.concatenate([actions, action], axis=-1)
            hs = np.concatenate([hs, next_h], axis=0)
            cs = np.concatenate([cs, next_c], axis=0)
        states = states[:, :-1]
        hs = hs[:-1]
        cs = cs[:-1]
        batch_states = np.concatenate([batch_states, states], axis=-1)
        batch_actions = np.concatenate([batch_actions, actions], axis=-1)
        batch_rewards = np.concatenate([batch_rewards, rewards], axis=-1)
        batch_hs = np.append(batch_hs, hs).reshape(-1, g_hidden)
        batch_cs = np.append(batch_cs, cs).reshape(-1, g_hidden)
    agent.generator.update(
        batch_states,
        batch_actions,
        batch_rewards,
        batch_hs,
        batch_cs
    )
    agent.inherit_weights(agent.generator, agent.rollouter)


def d_train():
    agent.generate_id_samples(
        agent.generator,
        T,
        sampling_num,
        id_output_data,
    )
    vocab.write_id2word(id_output_data, output_data)

    d_data = DataForDiscriminator(
        id_input_data,
        id_output_data,
        batch_size,
        T,
        vocab
    )

    env.discriminator.fit_generator(
        d_data,
        steps_per_epoch=None,
        epochs=1
    )


def sentences_history(episode, agent, T, vocab, sampling_num):
    id_output_history = os.path.join(
        'data',
        'adversarial_{}_id_generated_sentences.txt'.format(episode + 1)
    )
    output_history = os.path.join(
        'data',
        'adversarial_{}_generated_sentences.txt'.format(episode + 1)
    )
    agent.generate_id_samples(
        agent.generator,
        T,
        sampling_num,
        id_output_history
    )
    vocab.write_id2word(id_output_history, output_history)


def mc_search(step, states, action, next_h, next_c):
    reward_t = np.zeros([1, 1], dtype=np.float32)
    agent.rollouter.reset_rnn_state()
    if step < T - 1:
        agent.rollouter.set_rnn_state(next_h, next_c)
        for i in range(n_sampling):
            Y = agent.rollout(step, states, action)
            reward_t += env.discriminator.predict(Y) / n_sampling
    else:
        Y = np.concatenate([states[:, 1:], action], axis=-1)
        reward_t = env.discriminator.predict(Y)
    return reward_t


if __name__ == "__main__":
    pre_train()
    train()
