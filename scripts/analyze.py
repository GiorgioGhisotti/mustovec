#!/bin/python3

from gensim import corpora
from gensim.models import Word2Vec
import argparse
import json
from collections import defaultdict
import logging


def getCorpus(artist, data):
    corpus = []
    for song in data:
        if song["artist"] == artist["name"]:
            corpus.append(song["lyrics"])
    stoplist = set("for a of the and to in if oh oh- ooh ooh- - -- \_ _ . ? / ( )".split())
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


def getTexts(num_artists, artists_file, data_file):
    artists = []
    data = []
    texts = []
    with open(artists_file, "r") as af, open(data_file, "r") as df:
        artists = json.load(af)
        data = json.load(df)
    for artist in artists[:num_artists]:
        corpus = getCorpus(artist, data)
        texts.append(
            {
                "artist": artist["name"],
                "texts": corpus,
                "dictionary": corpora.Dictionary(corpus)
            }
        )
    return texts


def main():
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Model file")
    parser.add_argument("-a", "--artists", help="Artists file")
    parser.add_argument("-n", "--num", help="Number of artists to consider")
    parser.add_argument("-d", "--data", help="Data file")
    parser.add_argument("-c", "--config", help="Config file")
    args = parser.parse_args()

    config = []
    model_file = "./en.model"
    data_file = "./data/data.json"
    artists_file = "./data/artists.json"
    num_artists = 15
    config_file = args.config if args.config else "./config.json"
    try:
        with open(config_file, "r") as cf:
            config = json.load(cf)
        model_file = args.model if args.model else config["model_file"]
        data_file = args.data if args.data else config["data_file"]
        artists_file = args.artists if args.artists else config["artists_file"]
        num_artists = args.num if args.num else config["num_artists"]
    except IOError:
        print(
            "Warning: Could not read %s."
            % (config_file)
        )

    texts = getTexts(
        num_artists=num_artists,
        artists_file=artists_file,
        data_file=data_file
    )
    # Load keyed wikipedia vector model
    # model = Word2Vec.load(model_file).wv
    print(texts)


if __name__ == "__main__":
    main()
