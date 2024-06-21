import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to clean text by removing non-ASCII characters
def clean_text(text: str) -> str:
    return text.encode('ascii', 'ignore').decode('ascii')

# DEPRATED: Function to scrape the Wikipedia page for song names
def scrap_wiki_for_songnames(wiki_url: str) -> pd.DataFrame:
    # Fetch the content of the page
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the specific table with the given classes
    target_table = soup.find('table', {'class': 'plainrowheaders'})
    assert target_table, "Target table not found or empty"

    # Check if the table was found
    if target_table:
        print(f"Target table found.")
        # Extract table rows
        rows = []
        for row in target_table.find_all('tr')[1:]:
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.text.strip() for cell in cells]
            rows.append(cell_texts)
    else:
        print("Target empty")

    # Create a DataFrame from the extracted rows
    df = pd.DataFrame(rows, columns=['Title', 'Writer(s)', 'Album', 'Year','misc1', 'misc2'])

    # Only keep Title
    df = df[['Title']]

    # Remove first row
    df = df.iloc[1:]

    # List of various types of quotes to be removed
    quote_chars = ['"', '“', '”', '„', '‟', '❝', '❞', '❮', '❯', '〝', '〞', '〟','†']

    # Replace each type of quote character with an empty string
    for quote in quote_chars:
        df['Title'] = df['Title'].str.replace(quote, '')

    # replace , with .
    df['Title'] = df['Title'].str.replace(',', '.')

    # Convert the DataFrame to a string
    df.to_string(index=False)

    # Remove any non-ASCII characters
    df['Title'] = df['Title'].apply(clean_text)

    return df


def get_from_genius(endpoint: str, access_token: str) -> dict:
    # Make the GET request
    response = requests.get(endpoint, headers={'Authorization': 'Bearer ' + access_token})

    # Check if the request was successful
    if response.status_code == 200:
        # Process the response
        data = response.json()
        # Do something with the data
        return data
    else:
        print('Error:', response.status_code)
        return None

    
def get_artist_id(artist_name: str, access_token: str) -> int:
    search_endpoint = f'https://api.genius.com/search?q={artist_name}'
    data = get_from_genius(search_endpoint, access_token)
    return data['response']['hits'][0]['result']['primary_artist']['id']

