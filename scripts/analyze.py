#!/bin/python3

import numpy as np
import nltk
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import argparse
import json
import logging
import math
import re

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


def filterSong(song):
    out = re.sub(
        r"\.|\-|\(|\)|\–|\!|\?|\,", " ", song
    )
    tagged = nltk.pos_tag(nltk.word_tokenize(out))
    discard_tags = [
        "CC", "CD", "EX", "FW",
        "IN", "LS", "MD", "PRP",
        "PRP$", "TO", "UH", "SYM",
        "WDT", "WP", "WP$", "WRB"
    ]
    out = " ".join(w[0] for w in tagged if w[1] not in discard_tags)
    return out


def getCorpus(artist, data):
    corpus = []
    for song in data:
        lyrics = filterSong(song["lyrics"])
        if song["artist"].lower() == artist["name"].lower() and lyrics != []:
            corpus.append(
                {
                    "title": song["title"],
                    "lyrics": lyrics
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
    for artist in artists[:min(num_artists, len(artists))]:
        corpus = getCorpus(artist, data)
        if corpus != []:
            texts.append(
                {
                    "artist": artist["name"],
                    "songs": corpus,
                }
            )
    return (artists[:min(num_artists, len(artists))], texts)


def radiusOfGyration(center_of_mass, visited, visits):
    return [[math.sqrt(
        sum([abs(r[i] - center_of_mass[i]) for r in visited], 0)/visits
    )] for i in range(len(center_of_mass))]


def findRogs(model_file, artists_file, num_artists, data_file):
    logging.info("Running Radius of Gyration analysis")
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
        ] for a in range(min(num_artists, len(artists)))
    ]
    centers = [
        np.mean(means[n], axis=0) for n in range(
            min(num_artists, len(artists))
        )
    ]
    return [
        {
            "name": artists[i]["name"],
            "rogs": radiusOfGyration(
                center_of_mass=centers[i],
                visited=means[i],
                visits=len(means[i])
            )
        } for i in range(min(num_artists, len(artists)))
    ]


def averageRog(data_file):
    logging.info("Running Radius of Gyration average analysis")
    data = []
    with open(data_file, "r") as df:
        data = json.load(df)
    return [
        {
            "name": artist["name"],
            "average_rog": np.mean(artist["rogs"], axis=0)[0]
        } for artist in data
    ]


def vectors(model_file, artists_file, num_artists, data_file):
    logging.info("Running vector analysis")
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
            )for corpus in text["songs"]
        ] for text in texts
    ]
    centers = [
        np.mean(means[n], axis=0) for n in range(
            min(num_artists, len(artists))
        )
    ]
    return [
        {
            "artist": artists[i]["name"],
            "center": centers[i].tolist(),
            "vectors": [(mean.tolist()) for mean in means[i]]
        } for i in range(min(num_artists, len(artists)))
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Model file")
    parser.add_argument("-a", "--artists", help="Artists file")
    parser.add_argument("-n", "--num", help="Number of artists to consider")
    parser.add_argument("-d", "--data", help="Data file")
    parser.add_argument("-c", "--config", help="Config file")
    parser.add_argument("-o", "--out", help="Output file")
    parser.add_argument(
        "-t",
        "--atype",
        help="Analysis type (rog, avg_rog, vectors)"
    )
    args = parser.parse_args()

    out_file = "./data/rogs.json"
    model_file = "./en.model"
    data_file = "./data/data.json"
    artists_file = "./data/artists.json"
    num_artists = 15
    analysis_type = "rog"
    config_file = args.config if args.config else "./config.json"
    config = []
    logging.info("Attempting to read configuration from %s..." % (config_file))
    try:
        with open(config_file, "r") as cf:
            config = json.load(cf)
        out_file = args.out if args.out else config["out_file"]
        model_file = args.model if args.model else config["model_file"]
        data_file = args.data if args.data else config["data_file"]
        artists_file = args.artists if args.artists else config["artists_file"]
        num_artists = args.num if args.num else config["num_artists"]
        analysis_type = args.atype if args.atype else config["analysis_type"]
        logging.info("Configuration read from %s" % (config_file))
    except IOError:
        logging.warning(
            "Could not read %s"
            % (config_file)
        )

    if analysis_type == "rog":
        rogs = findRogs(model_file, artists_file, num_artists, data_file)
        if not args.out:
            if input(
                "Write output of Radius of Gyration analysis to %s? [y/N]" %
                (out_file)
            ).lower() != "y":
                return
        logging.info("Writing Radius of Gyration data to %s..." % (out_file))
        with open(out_file, "w") as of:
            json.dump(rogs, of)
            logging.info("Data written to %s" % (out_file))
    elif analysis_type == "avg_rog":
        avg_rogs = averageRog(data_file)
        if not args.out:
            if input(
                "Write Radius of Gyration averages to %s? [y/N]" %
                (out_file)
            ).lower() != "y":
                return
        logging.info(
            "Writing Radius of Gyration averages to %s..." % (out_file)
        )
        with open(out_file, "w") as of:
            json.dump(avg_rogs, of)
            logging.info("Data written to %s" % (out_file))
    elif analysis_type == "vectors":
        v = vectors(model_file, artists_file, num_artists, data_file)
        if not args.out:
            if input(
                "Write output of vector analysis to %s? [y/N]" %
                (out_file)
            ).lower() != "y":
                return
        logging.info("Writing vector data to %s..." % (out_file))
        with open(out_file, "w") as of:
            json.dump(v, of)
            logging.info("Data written to %s" % (out_file))


if __name__ == "__main__":
    main()
