import numpy as np
import pandas as pd
import os, sys
import glob
import io
import re
import csv
from tqdm import tqdm

import argparse

import spacy
nlp = spacy.load('ja_ginza')

from create_data_label import create_dummy, create_target, merge_data

def make_sentence(input_path, tokenizer):
    df = pd.read_json(input_path, lines=True, encoding='utf-8')
    df = df[~df['title'].str.contains('曖昧さ回避', case=False)]
    sentence_list = []
    for idx, article in tqdm(df.iterrows()):
        article_text = article['text']
        article_sentences = tokenize_article(article['text'], tokenizer)
        sentence_list = sentence_list + article_sentences[1:]
    return sentence_list

def remove_symbols_from_sentence(sentence):
    w = re.sub(r'(\d)([,.])(\d+)', r'\1\3', sentence)
    w = re.sub(r'\d+', '0', w)
    w = re.sub(r'[!-/:-@[-`{-~]', r'', w)
    w = re.sub(r'[「」()（）、＜＞・※*→↑←↓『』]', '', w)
    return w

def tokenize_article(text_article, tokenizer):
    sentences = []
    for t in text_article.strip().split('\n'):
        if (t == ''): continue
        for sentence in t.strip().split('。'):
            if (sentence == ''): continue
            sentence = remove_symbols_from_sentence(sentence)
            if (sentence == ''): continue
            words = tokenizer(sentence)
            sentences.append([w.orth_ for w in words])

    sentences.pop(0)
    return sentences

def create_data_wiki(args):

    row_data_dir = os.path.normpath(os.path.abspath(args.row_data_dir))
    row_data_files = glob.glob(os.path.join(row_data_dir, '*'))
    row_data_files.sort()

    negative_data_dir = os.path.join(os.path.abspath(args.negative_data_dir), row_data_dir.split('/')[-1])
    output_dir = os.path.join(os.path.abspath(args.output_data_dir), row_data_dir.split('/')[-1])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    delimiter = args.delimiter

    sentences_list = []

    for row_data_file in row_data_files:
        print("Processing {}".format(row_data_file))
        s = make_sentence(row_data_file, nlp)
        output_file = row_data_file.split('/')[-1]
        with open(os.path.join(output_dir, output_file), 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter, lineterminator='\n')
            writer.writerows(s)
    
    positive_data_paths = glob.glob(os.path.join(output_dir,"*"))

    for i, p_path in enumerate(positive_data_paths):
        filename = p_path.split('/')[-1]
        if not os.path.exists(os.path.join(negative_data_dir)):
            os.makedirs(negative_data_dir)
        negative_data_path = os.path.join(negative_data_dir, filename)
        print(p_path)
        print(negative_data_path)

        create_dummy(p_path, negative_data_path, delimiter=delimiter)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("row_data_dir", help='wikidata Extracter によって展開されたwikiデータのディレクトリ, 例: ./wikidata/AA/', type=str)
    parser.add_argument("--output_data_dir", help='分かち書きしたデータのパス default=./results/', default='./results/', type=str)
    parser.add_argument("--negative_data_dir", help='', default='./results/negative_data', type=str)
    parser.add_argument('--delimiter', help='', default=' ', type=str)
    args = parser.parse_args()

    create_data_wiki(args)