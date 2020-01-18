#!python3

import json
import argparse


def sort_artists(data):
    artists = []
    for song in data:
        insert = True
        for artist in artists:
            if artist["name"] == song["artist"]:
                artist["appearances"] += song["billboard"]
                insert = False
        if insert:
            artists.append(
                {"name": song["artist"], "appearances": song["billboard"]}
            )
    artists = sorted(artists, key=lambda artist: artist["appearances"])
    artists.reverse()
    return artists


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Data file")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()

    if not args.data:
        print("Please provide the path to a valid data file.")

    data_file = args.data
    output_path = args.output if args.output else "artists.json"
    data = []
    with open(data_file, "r") as df:
        data = json.load(df)
    data = sorted(data, key=lambda song: song["billboard"])
    data.reverse()

    output = sort_artists(data)
    print(output[:10])
    with open(output_path, "w") as of:
        json.dump(output, of)


if __name__ == "__main__":
    main()
