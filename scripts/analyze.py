#!/usr/bin/python3

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
    '''
    Filters out unwanted words (e.g. anything that isn't English,
    articles, etc.)
    '''
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
    for s in data:
        if s["artist"].lower() == artist["name"].lower():
            if len(filterSong(s["lyrics"])) > 0:
                corpus.append({
                    "title": s["title"].lower(),
                    "lyrics": filterSong(s["lyrics"])
                })
    return (artist, corpus)


def getTexts(num_artists, artists_file, data_file):
    '''
    Formats song data in a way that can be better processed
    '''
    artists = []
    data = []
    texts = []
    with open(artists_file, "r") as af, open(data_file, "r") as df:
        artists = json.load(af)
        data = json.load(df)
    corpora = Parallel(
        verbose=100, n_jobs=multiprocessing.cpu_count()
    )(
        delayed(getCorpus)(
            artist,
            data
        ) for artist in artists[:min(num_artists, len(artists))]
    )
    for (artist, corpus) in corpora:
        if corpus != []:
            texts.append(
                {
                    "artist": artist["name"],
                    "songs": corpus,
                }
            )
    return texts


def getGeometricCentre(model: KeyedVectors, text):
    doc = [word for word in text.split(" ") if word in model.vocab]
    if len(doc) == 0:
        return -1 * np.ones(len(model["hello"]))
    return np.mean(model[doc], axis=0)


def radiusOfGyration(center_of_mass, visited, visits):
    return [
        [
            math.sqrt(
                sum(
                    [
                        abs(
                            r[i] - center_of_mass[i]
                        ) for i in range(len(center_of_mass))
                    ],
                    0
                )/visits
            )
        ] for r in visited
    ]


def findCorpora(model_file, artists_file, num_artists, data_file):
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    logging.info("Extracting vectors")
    return getTexts(
        num_artists=num_artists,
        artists_file=artists_file,
        data_file=data_file
    )


def findVectors(model_file, artists_file, num_artists, data_file):
    '''
    Works out the geometric center of each artist as well as the mean
    vector means of each song
    '''
    artists = []
    texts = []
    with open(artists_file, "r") as af, open(data_file, "r") as df:
        texts = json.load(df)
        artists = json.load(af)[:len(texts)]
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
        np.mean(m, axis=0) for m in means
    ]
    return [
        {
            "artist": artists[i]["name"],
            "center": centers[i].tolist(),
            "vectors": [m.tolist() for m in means[i]]
        } for i in range(min(num_artists, len(artists)))
    ]


def findRogs(vectors):
    logging.info("Running Radius of Gyration analysis")
    rogs = Parallel(
        verbose=100, n_jobs=multiprocessing.cpu_count(), prefer="threads"
    )(
        delayed(
            lambda i : {
                "name": vectors[i]["artist"],
                "rogs": radiusOfGyration(
                    center_of_mass=vectors[i]["center"],
                    visited=vectors[i]["vectors"],
                    visits=1
                )
            }
        )(i) for i in range(len(vectors))
    )
    return rogs

def averageRog(rogs):
    logging.info("Running Radius of Gyration average analysis")
    return [
        {
            "name": artist["name"],
            "average_rog": np.mean(artist["rogs"], axis=0).tolist()
        } for artist in rogs
    ]


def writeToOut(out_file, data):
    '''
    Support function for file output
    '''
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
            "Writing data to %s..." % (out_file)
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
        "(corpora, vectors, rogs, avg_rogs)"
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
        num_artists = int(args.num) if args.num else config["num_artists"]
        analysis_type = args.atype if args.atype else config["analysis_type"]
        logging.info("Configuration read from %s" % (config_file))
    except IOError:
        logging.warning(
            "Could not read %s"
            % (config_file)
        )

    if analysis_type == "corpora":
        corpora = findCorpora(model_file, artists_file, num_artists, data_file)
        writeToOut(args.out, corpora)
    elif analysis_type == "vectors":
        v = findVectors(model_file, artists_file, num_artists, data_file)
        writeToOut(args.out, v)
    elif analysis_type == "rogs":
        vectors = []
        with open(data_file, "r") as v:
            vectors = json.load(v)
        rogs = findRogs(vectors)
        writeToOut(args.out, rogs)
    elif analysis_type == "avg_rogs":
        rogs = []
        with open(data_file, "r") as df:
            rogs = json.load(df)
        avg_rogs = averageRog(rogs)
        writeToOut(args.out, avg_rogs)
    else:
        logging.error("Invalid analysis type: %s" % (analysis_type))


if __name__ == "__main__":
    main()
