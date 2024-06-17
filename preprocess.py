import json
import pandas as pd

from src.preprocess_helper import clean_up_lyrics, remove_duplicate_songs
from src.helper import load_json

# Load your JSON data
input_filename = "output/greenday_lyrics.json"
output_filename = "output/greenday_lyrics_preprocessed.json"

data = load_json(input_filename)

# Load data as dataframe
df = pd.DataFrame(data.items(), columns=['url', 'lyrics'])

# Fix URLs by removing escape characters
df['url'] = df['url'].str.replace(r'\\/', '/')

# Remove duplicate songs
df = remove_duplicate_songs(df, verbose=False)

# Apply clean_up_lyrics function to the 'lyrics' column
df['cleaned_lyrics'] = df['lyrics'].apply(clean_up_lyrics)

print(f"Number of raw songs: {len(data)}")
print(f"Number of cleaned songs: {df.shape[0]}")

# Convert DataFrame to dictionary with 'url' as keys and 'cleaned_lyrics' as values
lyrics_dict = df.set_index('song_names')['cleaned_lyrics'].to_dict()
with open(output_filename, 'w') as f:
    json.dump(lyrics_dict, f, indent=4)
    
print(f"Saved preprocessed lyrics to {output_filename}")
