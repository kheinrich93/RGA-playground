import csv

from src.helper import scrap_wiki_for_songnames, output_csv


# Fetch songlist from URL of Band from Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_songs_recorded_by_Green_Day'

df = scrap_wiki_for_songnames(url)
output_csv(df, 'output/song_names.csv')

# fetch lyrics of those songs