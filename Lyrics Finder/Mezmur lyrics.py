import requests
from bs4 import BeautifulSoup
from docx import Document
import webbrowser
def generate_artist_url(artist_name, album_name=None, song_name=None):
    base_url = "https://wikimezmur.org/am/"

    # Capitalize first letter of each word
    artist_name = ' '.join(word.capitalize() for word in artist_name.split())

    # Replace spaces with underscores
    artist_name = artist_name.replace(" ", "_")

    # Replace underscores with capitalized letters after underscores
    artist_name = '_'.join(part.capitalize() for part in artist_name.split('_'))

    artist_url = base_url + artist_name + "/"

    if album_name:
        # Capitalize first letter of each word
        album_name = ' '.join(word.capitalize() for word in album_name.split())

        # Replace spaces with underscores
        album_name = album_name.replace(" ", "_")

        # Replace underscores with capitalized letters after underscores
        album_name = '_'.join(part.capitalize() for part in album_name.split('_'))

        album_url = artist_url + album_name + "/"
        artist_url = album_url

    if song_name:
        # Capitalize first letter of each word
        song_name = ' '.join(word.capitalize() for word in song_name.split())

        # Replace spaces with underscores
        song_name = song_name.replace(" ", "_")

        # Replace underscores with capitalized letters after underscores
        song_name = '_'.join(part.capitalize() for part in song_name.split('_'))

        song_url = artist_url + song_name
        artist_url = song_url
    print("--THIS IS THE URL FOR CHECKING___", artist_url)
    return artist_url
def empty_space_eliminator(text):
    text = text.get_text(separator='\n').strip()
    text = text.splitlines()

    # Remove empty lines
    non_empty_lines = [line for line in text if line.strip()]
    merged_text = '\n'.join(non_empty_lines)

    return merged_text


def scrape_lyrics(artist_url):
    result = requests.get(artist_url)
    soup = BeautifulSoup(result.text, 'lxml')

    # First, try to find lyrics in the first class
    lyrics_class1 = soup.find(class_="mw-parser-output")

    if lyrics_class1:
        scrape_lyrics.lyrics_text = empty_space_eliminator(lyrics_class1)
        print(scrape_lyrics.lyrics_text)

    elif not lyrics_class1:
        lyrics_class2 = soup.find('div', class_="poem")
        if lyrics_class2:
            scrape_lyrics.lyrics_text = empty_space_eliminator(lyrics_class2)
            print(scrape_lyrics.lyrics_text)

            # Process lyrics further, save them, etc.

    else:
        print("Sorry, lyrics couldn't be found in either class.")

while True:
    artist_name = input("Enter artist name (or type 'exit' to quit): ")
    # Check if the user wants to exit
    if artist_name.lower() == "exit":
        print("Exiting the program...")
        break

    album_name = input("Enter album name: ")
    song_name = input("Enter song name: ")

    # Use the generate_artist_url function to get the artist_url
    artist_url = generate_artist_url(artist_name, album_name, song_name)

    if artist_url:
        # Use the scrape_lyrics function to scrape lyrics using the obtained artist_url
        scrape_lyrics(artist_url)
        if scrape_lyrics.lyrics_text:
            doc = Document()
            doc.add_paragraph(scrape_lyrics.lyrics_text)
            doc.save("lyrics_output.docx")
            print("Lyrics saved as 'lyrics_output.docx'.")
            # Open the saved DOCX file
            webbrowser.open("lyrics_output.docx")
    else:
        print("Artist URL not found.")

# # Example usage:
# artist_url = "https://wikimezmur.org/am/Samuel_Tesfamichael/Misale_Yeleleh/Misale_Yeleleh"
# scrape_lyrics(artist_url)
