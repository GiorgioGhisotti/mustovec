#!/bin/python3
# Get all songs from given artists

import argparse
import lyricsgenius
import json
import sys
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Input data")
    parser.add_argument("-o", "--output", help="Set output file")
    parser.add_argument("-g", "--genius", help="Set genius access token")
    parser.add_argument("-n", "--number", help="Set number of artists")
    args = parser.parse_args()

    access_token = args.genius if args.genius else \
        "JW59dXoj6pHvcaHKGyUTpPwOl2FNQNfYuwZXvVFyJv7xWjs48UEQMD0sWm2jnJkp"
    path = args.output if args.output else "song_lyrics.json"
    data = args.data if args.data else "artists.json"
    num = int(args.number) if args.number else 15

    try:
        genius = lyricsgenius.Genius(access_token)
        genius.timeout = 1000000
    except Exception as e:
        print("%s, could not sign in to Genius." % (e))
        sys.exit(1)

    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print("%s, could not create folder at requested path!" % (e))
        sys.exit(1)

    top_artists = []
    with open(data, "r") as df:
        top_artists = json.load(df)

    genius_artists = []
    for artist in top_artists[:num]:
        while True:
            try:
                s = genius.search_artist(artist["name"], max_songs=10000)
                genius_artists.append(s)
                break
            except:
                pass
    genius.save_artists(artists=genius_artists, filename=path)


if __name__ == "__main__":
    main()
