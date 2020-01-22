# Mustovec

Scripts and material for a word2vec analysis of song lyrics.

## Requirements

You need python3 and an internet connection.

To install dependencies you can use pip:

```
pip install -r requirements.txt
```

## Usage

There are 6 scripts. All scripts output a help message when passed -h. All
data is saved in json format.

### scrape.py

Collects the author, title and lyrics of all songs on the weekly
top 100 song chart from Billboard.com, starting from the given date and
stopping after the given number of weeks.

### top_artists.py

Counts the number of occurrences of all artists in the data collected by
scrape.py.

### songs.py

Collects the entire discography of a given amount of top artists.

### merge.py

Merges the data collected by songs.py into one file.

### raw_merge.py

Converts the data collected by scrape.py into the same format as the output
of merge.py to allow for analysis.

### analyze.py

Performs all vector analysis on merged datasets.

### Example run

This is the sequence of commands to obtain the data used for my analysis.

From the project's root directory:
```
./scripts/scrape.py
./scripts/top_artists.py -d data/data.json -o data/artists.json
./scripts/songs.py -d data/artists.json -o lyrics_50 -n 50
./scripts/merge.py -p lyrics_50 -o data/lyrics_50.json
./scripts/raw_merge.py -d data/data.json -o data/raw_lyrics.json

  
./scripts/analyze.py -d ./data/lyrics_50.json -o ./data/corpora_50.json -n 50 -t corpora
./scripts/analyze.py -d ./data/corpora_50.json -o ./data/vectors_50.json -n 50 -t vectors
./scripts/analyze.py -d ./data/vectors_50.json -o ./data/deviations_50.json -n 50 -t deviations
./scripts/analyze.py -d ./data/deviations_50.json -o ./data/avg_deviations_50.json -n 50 -t avg_deviations
./scripts/analyze.py -d ./data/vectors_50.json -o ./data/overall_deviations_50.json -n 50 -t overall_deviations
./scripts/analyze.py -d ./data/overall_deviations_50.json -o ./data/overall_avg_deviations_50.json -n 50 -t avg_deviations

./scripts/analyze.py -d ./data/raw_lyrics.json -o ./data/raw_corpora.json -n 1784 -t corpora
./scripts/analyze.py -d ./data/raw_corpora.json -o ./data/raw_vectors.json -n 1784 -t vectors
./scripts/analyze.py -d ./data/raw_vectors.json -o ./data/raw_deviations.json -n 1784 -t deviations
./scripts/analyze.py -d ./data/raw_deviations.json -o ./data/raw_avg_deviations.json -n 1784 -t avg_deviations
./scripts/analyze.py -d ./data/raw_vectors.json -o ./data/raw_overall_deviations.json -n 1784 -t overall_deviations
./scripts/analyze.py -d ./data/raw_overall_deviations.json -o ./data/raw_overall_avg_deviations.json -n 1784 -t avg_deviations
```
