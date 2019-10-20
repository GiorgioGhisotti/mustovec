#!/bin/python3

import np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import argparse
import json
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
                        r"\.|\-|\(|\)|\–|\!|\?|\,", " ", song["lyrics"]
                    )
                }
            )
    return corpus


def getGeometricCentre(model: KeyedVectors, text):
    doc = [word for word in text if word in model.vocab]
    return np.mean(model[doc], axis=0)


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
    return (artists[:num_artists], texts)


def radiusOfGyration(center_of_mass, visited, visits):
    return [[math.sqrt(
        sum([abs(r[i] - center_of_mass[i]) for r in visited], 0)/visits
    )] for i in range(len(center_of_mass))]


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

    (artists, texts) = getTexts(
        num_artists=num_artists,
        artists_file=artists_file,
        data_file=data_file
    )
    # Load keyed wikipedia vector model
    model = Word2Vec.load(model_file).wv
    means = [
        [
            getGeometricCentre(
                model=model, text=corpus["lyrics"]
            )for corpus in texts[a]["songs"]
        ] for a in range(num_artists)
    ]
    centers = [
        np.mean(means[n], axis=0) for n in range(num_artists)
    ]
    rogs = [
        (
            artists[i]["name"],
            radiusOfGyration(
                center_of_mass=centers[i],
                visited=means[i],
                visits=len(means[i])
            )
        ) for i in range(num_artists)
    ]
    print(rogs)


if __name__ == "__main__":
    main()
