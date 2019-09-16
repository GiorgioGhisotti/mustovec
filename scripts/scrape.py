#!/bin/python3

import argparse
import lyricsgenius
import datetime
import re
import sys
import json
import urllib.request
from bs4 import BeautifulSoup
import time
import os

BILLBOARD = "https://www.billboard.com/charts/hot-100"


# Downloads Billboard top 100 list for given week, extracts relevant data
def get_top_songs(date):
    date_string = str(date).split()[0]
    print("Fetching top 100 data for the week of %s..." % (date_string))
    url = BILLBOARD + "/" + date_string
    while True:
        try:
            # Download Top 100 page
            req = urllib.request.Request(
                url,
                headers={'User-Agent': "Magic Browser"}
            )
            break
        except Exception as e:
            print("%s, trying again..." % (e))
            time.sleep(1)
    soup = BeautifulSoup(urllib.request.urlopen(req).read(), "html.parser")
    # Extract songs from divs
    songs = soup.find_all(
        lambda tag: tag.name == 'div' and
        tag.get('class') == ['item-details__title']
    )
    # Extract artists from divs
    artists = soup.find_all(
        lambda tag: tag.name == 'div' and
        tag.get('class') == ['item-details__artist']
    )
    s = []
    a = []
    # Parse songs into something usable
    for song in songs:
        s.append(
            re.sub(
                "&amp;",
                "&",
                re.sub(
                    "</div>",
                    "",
                    re.sub(
                        "<div .*?>",
                        "",
                        str(song)
                    )
                )
            )
        )
    # Parse artists into something usable
    for artist in artists:
        a.append(
            re.sub(
                "&amp;",
                "&",
                re.sub(
                    "</div>",
                    "",
                    re.sub(
                        "<div .*?>",
                        "",
                        str(artist)
                    )
                )
            )
        )
    return zip(s, a)


# Lyrics from genius.com
def get_lyrics(genius, artist, title):
    artist = artist.lower()
    title = title.lower()
    while True:
        try:
            lyrics_search = genius.search_song(title, artist)
            break
        except Exception as e:
            print("%s, trying again..." % (e))
            time.sleep(1)
    if lyrics_search is not None:
        lyrics = re.sub(r"\[.*?\]", "", lyrics_search.lyrics.lower())
        return lyrics
    else:
        for word in title.split():
            lyrics_search = genius.search_song(word, artist)
            if lyrics_search is not None:
                return lyrics_search.lyrics
        return ""


# Add song data to list - data is all data, tmpdate is only one week's data
def add_to_data(title, artist, service, genius, data, tmpdata):
    for song in data:
        if song["title"] == title and song["artist"] == artist:
            song[service] += 1
            tmpdata.append({
                "title": song["title"],
                "artist": song["artist"],
                "lyrics": song["lyrics"]
            })
            return
    lyrics = get_lyrics(genius, artist, title)
    data.append({
        "title": title,
        "artist": artist,
        service: 1,
        "lyrics": lyrics
    })
    tmpdata.append({
        "title": title,
        "artist": artist,
        "lyrics": lyrics
    })
    return


# Write json song data to file
def write_to_file(json_file, data):
    while True:
        try:
            with open(json_file, "w") as of:
                json.dump(data, of)
            break
        except Exception as e:
            print("%s, trying again..." % (e))
            time.sleep(1)


# Get and save song data
def scrape(genius, date, weeks, path):
    data = []
    tmpdata = []
    for i in range(weeks):
        top_songs = get_top_songs(date)
        for (title, artist) in top_songs:
            add_to_data(
                genius=genius,
                title=title,
                artist=artist,
                service="billboard",
                data=data,
                tmpdata=tmpdata
            )
        date_string = str(date).split()[0]
        date -= datetime.timedelta(days=7)
        print("Writing json data to file...")
        write_to_file(path + "/data" + date_string + ".json", tmpdata)
        tmpdata = []
    write_to_file(path + "/data.json", data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--weeks", help="Number of weeks to search")
    parser.add_argument("-s", "--start", help="Starting date (dd-mm-yyyy)")
    parser.add_argument("-o", "--outputpath", help="Set output path")
    parser.add_argument("-g", "--genius", help="Set genius access token")
    args = parser.parse_args()

    access_token = args.genius if args.genius else "JW59dXoj6pHvcaHKGyUTpPwOl2FNQNfYuwZXvVFyJv7xWjs48UEQMD0sWm2jnJkp"
    path = args.outputpath if args.outputpath else "data"
    date = datetime.datetime.strptime(
        args.start, "%d-%m-%Y") if args.start else datetime.datetime(2019, 9, 7)
    weeks = args.weeks if args.weeks else 520

    try:
        genius = lyricsgenius.Genius(access_token)
    except Exception as e:
        print("%s, could not sign in to Genius." % (e))
        sys.exit(1)

    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print("%s, could not create folder at requested path!" % (e))
        sys.exit(1)

    scrape(
        genius=genius,
        date=date,
        weeks=weeks,
        path=path
    )


if __name__ == "__main__":
    main()
