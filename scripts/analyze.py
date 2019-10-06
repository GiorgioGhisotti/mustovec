#!/bin/python3

from gensim import corpora
import np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import argparse
import json
from collections import defaultdict
import logging
import math
import re


def getCorpus(artist, data):
    corpus = []
    for song in data:
        if song["artist"].lower() == artist["name"].lower():
            corpus.append(
                {
                    "title": song["title"],
                    "lyrics": re.sub(
                        "\.|\-|\(|\)|\–|\!|\?|\,", " ", song["lyrics"]
                    )
                }
            )
    print(len(corpus))
    return corpus


def getGeometricCentre(model: KeyedVectors, text):
    doc = [model[word] for word in text if word in model.vocab]
    n = len(doc[0])
    out = model["hello"].copy()
    out.flags.writeable = True
    for i in range(n):
        sum = 0
        for d in doc:
            sum += d[i]
        out[i] = sum/n
    return out


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
                "songs": corpus,
            }
        )
    return texts


def radiusOfGyration(coordinates, center_of_mass, visited_locations, visits):
    return math.sqrt(sum([ri - center_of_mass for ri in visited_locations], 0))


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
    model = Word2Vec.load(model_file).wv
    print(type(model["hello"]))
    means = [
        [
            getGeometricCentre(
                model=model, text=corpus["lyrics"]
            )for corpus in text["songs"]
        ] for text in texts if text["artist"].lower() == "drake"
    ]
    print(type(means[0][0]))
    a = model.most_similar(means[0][0], topn=1)
    b = model.most_similar(means[0][1], topn=1)
    print(model.distance(a, b))


if __name__ == "__main__":
    main()
