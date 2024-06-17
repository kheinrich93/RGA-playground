import re
import pandas as pd

def clean_up_lyrics(lyrics: str) -> str:
    # Replace all newline characters with a space
    lyrics = lyrics.replace('\n', ' ')
    # Remove everything that is in [] brackets and the brackets themselves
    lyrics = re.sub(r'\[.*?\]', '.', lyrics)
    # Remove all unicode characters
    lyrics = re.sub(r'[^\x00-\x7F]+', ' ', lyrics)
    # Remove all special characters but keep , and .
    lyrics = re.sub(r'[^\w\s\.,]', '', lyrics)
    # Remove unnecessary spaces
    lyrics = re.sub(r'\s+', ' ', lyrics)
    # Remove . at the beginning and end
    lyrics = lyrics.strip('.')
    # Remove space at the beginning and end
    lyrics = lyrics.strip()
    # Replace  " . " with ". "
    lyrics = lyrics.replace(' . ', '. ')

    return lyrics



def remove_duplicate_songs(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    # remove all rows where url does not start with https://genius.com/Green-day to exclude cover versions
    df = df[df['url'].str.contains('https://genius.com/Green-day')]

    # create new empty column 'song_names'
    df.loc[:, 'song_names'] = df['url'].str.replace('https://genius.com/Green-day-', '', regex=False)

    # Removing specific substrings from 'song_names' column
    df.loc[:, 'song_names'] = df['song_names'].str.replace('-lyrics', '', regex=False)
    df.loc[:, 'song_names'] = df['song_names'].str.replace('-annotated', '', regex=False)
    df.loc[:, 'song_names'] = df['song_names'].str.replace('-demo', '', regex=False)

    # create list of indexes to remove
    to_remove = []

    # reset index
    df = df.reset_index(drop=True)

    # go through all rows and compare the current with the next row, if they are the same, remove the current row 
    row_to_keep = df['song_names'].iloc[0]
    for i in range(len(df)-1):
        # if the substring is part of the next row, remove i row
        print(f'Compare {row_to_keep} with {df["song_names"].iloc[i+1]}') if verbose else None
        if row_to_keep in df['song_names'].iloc[i+1]:
            to_remove.append(i+1)
            print(f"Will remove row {i+1} with url {df['song_names'].iloc[i+1]}") if verbose else None
        else:
            row_to_keep = df['song_names'].iloc[i+1]

    # remove all rows where to_remove is True
    df = df[~df.index.isin(to_remove)]
    # reset index
    df = df.reset_index(drop=True)
    print(df['song_names'].head(10)) if verbose else None

    print("Finished removing duplicates. Added column 'song_names' with cleaned song names.")

    return df