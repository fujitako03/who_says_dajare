import os, sys, glob
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm

def run(args):
    true_data_dir = args.positive_data
    results_data_dir = args.results_path

    true_data_path = glob.glob(os.path.join(true_data_dir, '*.txt'))

    for t_path in tqdm(true_data_path):
        words = []
        sentence_lengh = []
        with open(t_path, 'r') as f:
            for s in f.readlines():
                new_line = s.strip().split()
                sentence_lengh.append(len(new_line))
                words = words + s.strip().split()

        filename = t_path.split('/')[-1]
        filename = 'negative_'+filename
        result_path = os.path.join(results_data_dir, filename)
        with open(result_path, 'w') as f:
            for i, s_len in enumerate(sentence_lengh):
                fake_sentence = np.random.choice(words, size=s_len)
                if i != len(sentence_lengh)-1:
                    f.write(' '.join(fake_sentence)+'\n')
                else:
                    f.write(' '.join(fake_sentence))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive_data", help='', default='../data/aozorabunko/train/positive_data/',type=str)
    parser.add_argument("--results_path", help='',default='../data/aozorabunko/train/negative_data', type=str)
    run(parser.parse_args())