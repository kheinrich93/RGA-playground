import pandas as pd

from src.helper import scrap_wiki_for_songnames

# Fetch songlist from URL of Band from Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_songs_recorded_by_Green_Day'

df = scrap_wiki_for_songnames(url)
df.to_csv('output/song_names.csv', index=False)

# Fetch lyrics of those songs
# load csv file 
df = pd.read_csv('output/song_names.csv')
print(df.head())