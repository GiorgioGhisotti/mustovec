#!/bin/python3

import gensim
from gensim import corpora
from gensim.models import Word2Vec
from gensim.models.word2vec import Text8Corpus
from gensim.models.phrases import Phrases, Phraser
import argparse
import json
from collections import defaultdict
import logging
from pprint import pprint


def getCorpus(data_path):
    corpus = []
    with open(data_path, "r") as df:
        data = json.load(df)
        for song in data:
            corpus.append(song["lyrics"])
    stoplist = set("for a of the and to in if ooh".split())
    texts = [
        [word for word in lyric.lower().split() if word not in stoplist]
        for lyric in corpus
    ]
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [
        [token for token in text if frequency[token] > 1]
        for text in texts
    ]
    return texts


def getDictionary(texts):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lsi = gensim.models.lsimodel.LsiModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=100
    )
    lsi.print_topics(10)
    lda = gensim.models.ldamodel.LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=100,
        update_every=1,
        passes=1
    )
    lda.print_topics(10)


def main():
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Model path")
    parser.add_argument("-d", "--data", help="Data path")
    args = parser.parse_args()

    model_path = args.model if args.model else "en.model"
    data_path = args.data if args.data else "data.json"
    
    texts = getCorpus(data_path)
    getDictionary(texts)


if __name__ == "__main__":
    main()
