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
from joblib import Parallel, delayed
import multiprocessing

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
    logging.info("Getting corpus for artist %s" % (artist["name"]))
    corpus = Parallel(verbose=100, n_jobs=multiprocessing.cpu_count())(
        delayed(
            lambda song : {
                "title": s["title"].lower(),
                "lyrics": filterSong(s["lyrics"])
            }
        )(s) for s in data if s["artist"].lower() == artist["name"].lower()
    )
    return corpus


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


def getGeometricCentre(model: KeyedVectors, text):
    doc = [word for word in text if word in model.vocab]
    return np.mean(model[doc], axis=0)


def radiusOfGyration(center_of_mass, visited, visits):
    return [[math.sqrt(
        sum([abs(r[i] - center_of_mass[i]) for r in visited], 0)/visits
    )] for i in range(len(center_of_mass))]


def findVectors(model_file, artists_file, num_artists, data_file):
    logging.info("Extracting vectors")
    (artists, texts) = getTexts(
        num_artists=num_artists,
        artists_file=artists_file,
        data_file=data_file
    )
    # Load keyed wikipedia vector model
    logging.info("Loading vectors")
    model = Word2Vec.load(model_file).wv
    logging.info("Working out means")
    means = [
        [
            getGeometricCentre(
                model=model, text=corpus["lyrics"]
            )for corpus in text["songs"]
        ] for text in texts
    ]
    logging.info("Working out centers")
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


def findRogs(vectors):
    logging.info("Running Radius of Gyration analysis")
    all_means = []
    for mean in vectors:
        for m in mean["vectors"]:
            all_means.append(m)
    logging.info("Working out rogs")
    return [
        {
            "name": vectors[i]["artist"],
            "rogs": radiusOfGyration(
                center_of_mass=vectors[i]["center"],
                visited=all_means,
                visits=len(all_means)
            )
        } for i in range(len(vectors))
    ]


def averageRog(rogs):
    logging.info("Running Radius of Gyration average analysis")
    return [
        {
            "name": artist["name"],
            "average_rog": np.mean(artist["rogs"], axis=0)[0]
        } for artist in rogs
    ]


def writeToOut(out_file, data):
    if not out_file:
        out_file = input("Output file: ")
    confirm = input(
        "Data will be written to %s. Confirm? [y/N/cancel] " %
        (out_file)
    ).lower()
    while confirm != "y":
        if confirm == "cancel":
            logging.warning("Aborting operation. No data was written to file.")
            return
        out_file = input("Output file: ")
        confirm = input(
            "Data will be written to %s. Confirm? [y/N/cancel] " %
            (out_file)
        ).lower()
    with open(out_file, "w") as of:
        logging.info(
            "Writing Radius of Gyration averages to %s..." % (out_file)
        )
        json.dump(data, of)
    logging.info("Data written to %s" % (out_file))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze dataset"
    )
    parser.add_argument("-m", "--model", help="Model file")
    parser.add_argument("-a", "--artists", help="Artists file")
    parser.add_argument("-n", "--num", help="Number of artists to consider")
    parser.add_argument("-d", "--data", help="Data file")
    parser.add_argument("-c", "--config", help="Config file")
    parser.add_argument("-o", "--out", help="Output file")
    parser.add_argument(
        "-t",
        "--atype",
        help="Analysis type " +
        "(full, vectors, rog, avg_rog, vectors+rog, rog+avg_rogs)"
    )
    args = parser.parse_args()

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

    if analysis_type == "full":
        vectors = findVectors(model_file, artists_file, num_artists, data_file)
        rogs = findRogs(vectors)
        avg_rogs = averageRog(rogs)
        writeToOut(args.out, avg_rogs)
    elif analysis_type == "vectors+rogs":
        vectors = findVectors(model_file, artists_file, num_artists, data_file)
        rogs = findRogs(vectors)
        writeToOut(args.out, rogs)
    elif analysis_type == "rogs+avg_rogs":
        vectors = []
        with open(data_file, "r") as v:
            vectors = json.load(v)
        rogs = findRogs(vectors)
        avg_rogs = averageRog(rogs)
        writeToOut(args.out, avg_rogs)
    elif analysis_type == "vectors":
        v = findVectors(model_file, artists_file, num_artists, data_file)
        writeToOut(args.out, v)
    elif analysis_type == "rog":
        vectors = []
        with open(data_file, "r") as v:
            vectors = json.load(v)
        rogs = findRogs(vectors)
        writeToOut(args.out, rogs)
    elif analysis_type == "avg_rog":
        rogs = []
        with open(data_file, "r") as df:
            rogs = json.load(df)
        avg_rogs = averageRog(rogs)
        writeToOut(args.out, avg_rogs)
    else:
        logging.error("Invalid analysis type: %s" % (analysis_type))


if __name__ == "__main__":
    main()
