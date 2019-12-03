import os,sys
import numpy as np

sys.path.append('../../notebook/scripts/modules/')
from datagenerator import Vocab

def create_dummy(input_data_path, output_data_path, delimiter=' '):

    vocab = Vocab(input_data_path, delimiter=delimiter)

    words = list(vocab.id2word.values())
    n_words = [len(s) for s in vocab.sentences]

    output_data_dir = os.path.dirname(output_data_path)

    if not os.path.exists(output_data_dir):
        os.makedirs(output_data_dir)

    with open(output_data_path, mode='w', encoding='utf-8') as output_file:
        for i, n_word in enumerate(n_words):
            dummy_sentence = np.random.choice(words, size=n_word, replace=False)
            if not i == len(n_words) - 1:
                output_file.write(delimiter.join(dummy_sentence)+'\n')
            else:
                output_file.write(delimiter.join(dummy_sentence))

def create_target(input_data_path, label, output_data_path):
    with open(input_data_path, 'r', encoding='utf-8') as f:
        labels = [str(label) for l in f.readlines()]

    with open(output_data_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(labels))

def merge_data(file1, file2, output_file):

    with open(output_file, 'w', encoding='utf-8') as f:
        with open(file1, 'r', encoding='utf-8') as read_file:
            f.write(read_file.read())
        with open(file2, 'r', encoding='utf-8') as read_file:
            f.write(read_file.read())

if __name__ == '__main__':

    positive_data_path = '../data/fix_wakachi_wikidata/AA/wiki_00'
    positive_label_path = '../data/test_data/positive_label.txt'
    negative_data_path  = '../data/test_data/dummy_data.txt'
    negative_label_path = '../data/test_data/negative_label.txt'
    delimiter = ' '
    positive_label = 1
    negative_label = 0
    output_data_path = '../data/test_data/sentence_data.txt'
    output_label_path = '../data/test_data/sentence_label.txt'

    create_dummy(positive_data_path, negative_data_path, delimiter=delimiter)
    merge_data(positive_data_path, negative_data_path, output_data_path)
    create_target(positive_data_path, positive_label, positive_label_path)
    create_target(negative_data_path, negative_label, negative_label_path)
    merge_data(positive_label_path, negative_label_path, output_label_path)