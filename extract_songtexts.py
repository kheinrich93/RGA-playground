import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


from src.helper import get_artist_id, get_access_token

# TODO: check for duplicates of songs and quantity


access_token = get_access_token(filename = 'auth_tokens/genius.json')

# Construct the API endpoint to get songs by the artist
artist_name = 'Green Day'
artist_id = get_artist_id(artist_name, access_token)
artist_songs_endpoint = f'https://api.genius.com/artists/{artist_id}/songs'

# Make the GET request to get songs by the artist
response = requests.get(artist_songs_endpoint, headers={'Authorization': 'Bearer ' + access_token})

lyrics_store = {} 
# Check if the request was successful
if response.status_code == 200:
    # Process the response to get song titles
    data = response.json()
    songs = data['response']['songs']

    # First n songs for debugging
    #songs = songs[:10]

    print(f"Found {len(songs)} songs")

    # Extract lyric 'path' from songs 
    song_lyric_urls = [f"https://genius.com{song['path']}" for song in songs]
    

    for song_lyric_url in tqdm(song_lyric_urls):
        # Make a GET request to the song URL to scrape the lyrics
        lyrics_response = requests.get(song_lyric_url)
        if lyrics_response.status_code == 200:
            soup = BeautifulSoup(lyrics_response.text, 'html.parser')
            # Check if lyrics exist on the page
            lyrics_div = soup.find('div', attrs={'data-lyrics-container': 'true'})
            if lyrics_div:
                # Extract and store lyrics
                lyrics_store[song_lyric_url] = lyrics_div.get_text(separator='\n')
else:
    print('Error:', response.status_code)

# save lyrics to a file
with open('output/lyrics.json', 'w') as f:
    json.dump(lyrics_store, f)

