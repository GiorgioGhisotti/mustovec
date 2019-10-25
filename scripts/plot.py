#!/bin/python3

import json
import argparse
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


def plot(data_file):
    data = []
    with open(data_file, "r") as df:
        data = json.loads(df)
    embedded_data = [
        {
            "name": artist["artist"],
            "center": TSNE().fit_transform(artist["center"]),
            "vectors": [
                TSNE().fit_transform(np.array(v)) for v in artist["vectors"]
            ]
        } for artist in data
    ]
    _, axs = plt.subplots()
    for artist in embedded_data:
        axs.scatter(artist["vectors"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Data file")
    args = parser.parse_args()

    data_file = args.data if args.data else "data/vectors.json"
    plot(data_file)


if __name__ == "__main__":
    main()
