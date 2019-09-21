#!/bin/python3

import json
import os
import re

data = []
for json_file in os.listdir():
    with open(json_file, "r") as lf:
        raw = json.load(lf)
        lyrics = raw["songs"][0]
        print(lyrics)
        lyrics["artist"] = raw["artist"]
        if lyrics["lyrics"] is not None:
            lyrics["lyrics"] = re.sub(
                r"\[.*?\]",
                "",
                lyrics["lyrics"]
            )
            lyrics_new = {
                "artist": lyrics["artist"],
                "title": lyrics["title"],
                "lyrics": lyrics["lyrics"]
            }
            data.append(lyrics_new)
with open("lyrics.json", "w") as of:
    json.dump(data, of)
