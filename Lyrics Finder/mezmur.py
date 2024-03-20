import requests
from bs4 import BeautifulSoup



url = "https://onlinemezmur.com/song_lyrics.php?song_id=347"
result = requests.get(url)
doc = BeautifulSoup(result.text, "html.parser")
# print(doc.prettify())
#
# amharic=doc.find("body")
# print(amharic)
elements_with_vline = doc.find_all(string="vline")

# Print the found elements
for element in elements_with_vline:
    print(element)
