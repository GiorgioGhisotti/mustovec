#!/usr/bin/python3

import json
import os
import re
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--d", help="Data file")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()
    data = args.data if args.data else "data/data.json"
    out = args.output if args.output else "raw_lyrics.json"
    data = []
    with open(path, "r") as lf:
        raw = json.load(lf)
        for lyrics in raw:
            if lyrics["lyrics"] is not None:
                lyrics["lyrics"] = re.sub(
                    r"\[.*?\]",
                    "",
                    lyrics["lyrics"]
                )
                lyrics["lyrics"] = re.sub(
                    r"[,\(\)-]",
                    "",
                    lyrics["lyrics"]
                )
                lyrics_new = {
                    "artist": lyrics["artist"],
                    "title": lyrics["title"],
                    "lyrics": lyrics["lyrics"]
                }
            data.append(lyrics_new)
    with open(out, "w") as of:
        json.dump(data, of)


if __name__ == "__main__":
    main()
