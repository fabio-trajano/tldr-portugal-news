import requests
from bs4 import BeautifulSoup
from datetime import datetime
import database

RSS_FEEDS = [
    'https://feeds.publico.pt/rss',
    'https://expresso.pt/rss',
    'https://observador.pt/feed/',
    'https://www.dn.pt/rss',
    'https://www.jn.pt/rss',
    'https://www.rtp.pt/noticias/index/rss.xml'
]

def fetch_article_content(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        art = soup.find('article')
        ps = art.find_all('p') if art else soup.find_all('p')
        return '\n'.join(p.get_text() for p in ps)
    except Exception:
        return ''

def scrape():
    new = []
    for rss in RSS_FEEDS:
        r = requests.get(rss, timeout=5)
        soup = BeautifulSoup(r.content, 'xml')
        for item in soup.find_all('item'):
            t = item.title.text
            u = item.link.text
            pd = item.pubDate.text if item.pubDate else ''
            content = fetch_article_content(u)
            aid = database.insert_article(t, u, content, pd)
            if aid:
                new.append(aid)
    return new
