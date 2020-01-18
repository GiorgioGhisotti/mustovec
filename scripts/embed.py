#!/usr/bin/python3

import json
import argparse
import numpy as np
from sklearn.manifold import TSNE
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


def embed(data_file):
    data = []
    centers = []
    vectors = []
    with open(data_file, "r") as df:
        data = json.load(df)
    for artist in data:
        centers.append(artist["center"])
        for v in artist["vectors"]:
            vectors.append(v)
    for v in vectors:
        centers.append(v)
    embedded = TSNE().fit_transform(np.array(centers))
    embedded_data = [
        {
            "name": data[i]["artist"],
            "center": embedded[i],
            "vectors": [
                v for v in embedded[
                    len(data)+i:len(data)+len(data[i]["vectors"])+1
                ]
            ]
        } for i in range(len(data))
    ]
    embedded_data = [
        {
            "name": ed["name"],
            "center": [
                ar.tolist() for ar in ed["center"]
            ],
            "vectors": [
                [
                    ar.tolist() for ar in v
                ] for v in ed["vectors"]
            ]
        } for ed in embedded_data
    ]
    return embedded_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Data file")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()

    data_file = args.data if args.data else "data/vectors.json"
    output_file = args.output if args.output else "data/embedded_vectors.json"
    evs = embed(data_file)
    with open(output_file, "w") as of:
        logging.info("Writing embedded data to %s..." % (output_file))
        json.dump(evs, of)


if __name__ == "__main__":
    main()
