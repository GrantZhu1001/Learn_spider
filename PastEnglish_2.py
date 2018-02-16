import re
from bs4 import BeautifulSoup

f = open('test.html','r',encoding='utf-8')
text = f.read()

soup = BeautifulSoup(text, 'lxml')
for br in soup.select('br'):
    print(br.get_text())
