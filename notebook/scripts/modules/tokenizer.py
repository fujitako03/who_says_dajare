import numpy as np
import pandas as pd
import os, sys
import glob
import io
import re
import csv

from abc import ABCMeta, abstractmethod

import spacy

class Tokenizer(metaclass=ABCMeta):

    @abstractmethod
    def tokenize_sentence(self, sentence):
        pass

class TokenizerSpacy(Tokenizer, object):
    def __init__(self):
        self._tokenizer = spacy.load('ja_ginza')

    def tokenize_sentence(self, sentence):
        doc = self._tokenizer(sentence)
        sentence = doc.sents.__next__()
        return [token.orth_ for token in sentence]