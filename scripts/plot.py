#!/bin/python3

import matplotlib.pyplot as plt
import matplotlib.collections as collections
import argparse
import numpy as np
import math
import json
from matplotlib import cm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Data file")
    args = parser.parse_args()
    data_file = args.data if args.data else "data/embedded_vectors.json"

    data = []
    with open(data_file, "r") as df:
        data = json.load(df)
    centers_x = [d["center"][0] for d in data]
    centers_y = [d["center"][1] for d in data]
    plt.scatter(
        centers_x, centers_y,
        c=np.linspace(0.0, 1.0, len(centers_x)),
        cmap=cm.get_cmap("gist_rainbow")
    )
    for i in range(max(len(d["vectors"]) for d in data)):
        vecs_x = [d["vectors"][i][0] if len(d["vectors"]) > i else None for d in data]
        vecs_y = [d["vectors"][i][1] if len(d["vectors"]) > i else None for d in data]
        plt.scatter(
            vecs_x, vecs_y,
            c=np.linspace(0.0, 1.0, len(vecs_x)),
            cmap=cm.get_cmap("gist_rainbow")
        )
    plt.show()

    
if __name__ == "__main__":
    main()