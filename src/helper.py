import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to clean text by removing non-ASCII characters
def clean_text(text: str) -> str:
    return text.encode('ascii', 'ignore').decode('ascii')

# Function to export the DataFrame to a CSV file, native csv function (.to_csv) does not work cause of special characters
def output_csv(df: pd.DataFrame, output_file: str) -> None:
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        # Write header
        file.write('Title\n')
        # Write each row
        for title in df['Title']:
            file.write(f'{title}\n')
    print(f"Exported to {output_file}")


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

    # Convert the DataFrame to a string
    df.to_string(index=False)

    # Remove any non-ASCII characters
    df['Title'] = df['Title'].apply(clean_text)

    return df

    