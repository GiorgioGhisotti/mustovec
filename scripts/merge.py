#!/bin/python3

import json
import os
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Lyrics folder path")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()
    path = args.path if args.path else "."
    out = args.output if args.output else "lyrics.json"
    data = []
    for json_file in os.listdir(path=path):
        with open(json_file, "r") as lf:
            raw = json.load(lf)
            print(json_file)
            songs = raw["songs"]
            artist = raw["name"]
            for lyrics in songs:
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
                        "artist": artist,
                        "title": lyrics["title"],
                        "lyrics": lyrics["lyrics"]
                    }
                data.append(lyrics_new)
    with open("lyrics.json", "w") as of:
        json.dump(data, of)


if __name__ == "__main__":
    main()
