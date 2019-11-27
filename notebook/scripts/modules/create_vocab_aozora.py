import os
import sys 
import glob
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import csv

from datagenerator import Vocab, DataForGenerator

def train(args):
    positive_data_dir = args.positive_data_dir
    negative_data_dir = args.negative_data_dir
    results_data = args.result_dir

    positive_data_path = [p for p in glob.glob(os.path.join(positive_data_dir, "*.txt"), recursive=True) 
                            if os.path.isfile(p)]
    negative_data_path = [p for p in glob.glob(os.path.join(negative_data_dir, "*.txt"), recursive=True) 
                            if os.path.isfile(p)]

    positive_data_path.sort()

    negative_data_path.sort()

    vocab = Vocab()

    for d in positive_data_path + negative_data_path:
        print("Loading " + d)
        sentences = []
        with open(d, 'r', encoding='utf-8') as f:
            for i, l in enumerate(f.readlines()):
                l = l.split()
                sentences.append(l)

        vocab.update_vocab(sentences)

    with open(results_data, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        for w,id in vocab.word2id.items():
            writer.writerow([w, id])

    print(len(vocab.word2id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("positive_data_dir", help="", type=str)
    parser.add_argument("negative_data_dir", help="", type=str)
    parser.add_argument('--result_dir', default='./tmp/vocab.csv')
    args = parser.parse_args()

    train(args)