import requests
from bs4 import BeautifulSoup
import random
website="https://www.azlyrics.com/n/nf.html"
link=requests.get(website)

soup=BeautifulSoup(link.text,'lxml')
songlinks=soup.find_all('div',class_="listalbum-item")
urls=[]

for song in songlinks:
    urls.append(song.find('a'))
# for url in urls:
#     print(url['href'])
for i in range(len(urls)):
    urls[i]['href']='https://www.azlyrics.com/'+ urls[i]['href']
for url in urls:
    print(url['href'])

randomsong=random.choice(urls)['href']
randomlink=requests.get(randomsong)
soup=BeautifulSoup(randomlink.text,'lxml')

lyrics=soup.find(class_="col-xs-12 col-lg-8 text-center")
lyrics=lyrics.get_text(separator='\n').strip()
lyrics=lyrics[lyrics.find('\n\n\n\n')+5:lyrics.find('Submit Corrections')]
lyrics=lyrics.splitlines()

a=[]

for i in range(len(lyrics)):
    if lyrics[i]=='':
        a.append(i)
for num in a:
    lyrics.remove('')
lyrics.pop()
merged_lyrics = '\n'.join(lyrics)
print(merged_lyrics)