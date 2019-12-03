import os, sys, glob
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm


def run(args):
    row_data_path = args.row_data_path
    results_path = args.results_path

    df_row = pd.read_csv(row_data_path, index_col=[0,1,2],usecols=range(6), header=None)

    file_index = np.unique(np.array(df_row.index.get_level_values(level=0)))

    for i, f_idx in tqdm(enumerate(file_index)):
        df_per_file = df_row.loc[f_idx,:]
        sentence_index = np.unique(np.array(df_per_file.index.get_level_values(level=0).values))
        sentences_matrix = []
        for s_idx in sentence_index:
            df_per_row = df_per_file.loc[s_idx]
            df_per_row = df_per_row[df_per_row[4]!='記号']
            word_index = np.unique(np.array(df_per_row.index.get_level_values(level=0).values))
            if len(word_index) != 0:
                sentence_array = []
                for w_idx in word_index:
                    if df_per_row.loc[w_idx, 5] != '数':
                        sentence_array.append(df_per_row.loc[w_idx, 3])
                    else:
                        sentence_array.append('0')
                sentences_matrix.append(sentence_array)

        filename = f_idx.split('.')[0]
        with open(os.path.join(results_path, filename+'.txt'), 'w') as file:
            for l in sentences_matrix:
                file.writelines(' '.join(l)+'\n')
        print('Saved at ', os.path.join(results_path, filename+'.txt'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--row_data_path", help='', default='../data/aozorabunko/row_data/utf8_all.csv',type=str)
    parser.add_argument("--results_path", help='',default='../data/aozorabunko/wakachi_aozora', type=str)
    run(parser.parse_args())