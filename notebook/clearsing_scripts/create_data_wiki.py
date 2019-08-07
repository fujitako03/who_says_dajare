import numpy as np
import pandas as pd
import os, sys
import glob
import io
import re
import csv

import spacy
nlp = spacy.load('ja_ginza')

output_path = './results/'

jsondata_path = glob.glob('../data/wikidata/extracted_data/*', recursive=False)
jsondata_path.sort()

def make_sentence_csv(input_path, output_path, tokenizer):
    df = pd.read_json(input_path, lines=True, encoding='utf-8')
    df = df[~df['title'].str.contains('曖昧さ回避', case=False)]
    sentence_list = []
    for idx, article in df.iterrows():
        article_text = article['text']
        article_sentences = tokenize_article(article['text'], tokenizer)
        sentence_list = sentence_list + article_sentences[1:]
    if not output_path is None:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines('\n'.join(sentence_list))
    return sentence_list

def remove_symbols_from_sentence(sentence):
    w = re.sub(r'(\d)([,.])(\d+)', r'\1\3', sentence)
    w = re.sub(r'\d+', '0', w)
    w = re.sub(r'[!-/:-@[-`{-~]', r'', w)
    w = re.sub(u'[「」（）、＜＞・※*→↑←↓]『』', '', w)
    return w

def tokenize_article(text_article, tokenizer):
    sentences = []
    for t in text_article.strip().split('\n'):
        if t != '':
            for sentence in t.strip().split('。'):
                if sentence != '':
                    sentence = remove_symbols_from_sentence(sentence)
                    if sentence != '':
                        words = tokenizer(sentence)
                        sentences.append([w.orth_ for w in words])

    sentences.pop(0)
    return sentences

sentences_list = []
for js_path in jsondata_path[1:3]:
    files_path = glob.glob(os.path.join(js_path, '*'))
    files_path.sort()
    for f in files_path:
        # print(f)
        s = make_sentence_csv(f, None, nlp)
        result_dir = os.path.join(output_path, os.path.basename(os.path.dirname(f)))
        result_filename = os.path.basename(f)
        print(os.path.join(result_dir, result_filename+'.csv'))
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        with open(os.path.join(result_dir, result_filename+'.csv'), 'w', encoding='utf-8') as output_file:
            writer = csv.writer(output_file, lineterminator='\n')
            writer.writerows(s)
