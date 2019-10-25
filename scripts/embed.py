#!/bin/python3

import json
import argparse
import numpy as np
from sklearn.manifold import TSNE
from joblib import Parallel, delayed


def embed(data_file, jobs):
    data = []
    with open(data_file, "r") as df:
        data = json.load(df)
    embedded_data = [
        {
            "name": artist["artist"],
            "center": TSNE().fit_transform(
                np.array(artist["center"]).reshape(-1, 1).tolist()
            ),
            "vectors": [
                Parallel(n_jobs=jobs, verbose=100)(
                    delayed(TSNE().fit_transform)(
                        np.array(v).reshape(-1, 1).tolist()
                    ) for v in artist["vectors"]
                )
            ]
        } for artist in data
    ]
    return embedded_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Data file")
    parser.add_argument("-j", "--jobs", help="Number of jobs")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()

    data_file = args.data if args.data else "data/vectors.json"
    jobs = int(args.jobs) if args.jobs and int(args.jobs) > 0 else 1
    output_file = args.output if args.output else "data/embedded_vectors.json"
    evs = embed(data_file, jobs)
    with open(output_file, "w") as of:
        json.dump(evs, of)


if __name__ == "__main__":
    main()
