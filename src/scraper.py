import requests
import xml.etree.ElementTree as ET
from dateutil import parser
from datetime import datetime
from zoneinfo import ZoneInfo

from database import init_db, get_connection


FEED_URL = 'https://www.noticiasaominuto.com/rss/ultima-hora'
NUM_LATEST = 5


def fetch_latest(n=NUM_LATEST):
    """Busca itens do RSS, ordena por pubDate e retorna os n mais recentes."""
    resp = requests.get(FEED_URL)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = root.findall('./channel/item')

    records = []
    for item in items:
        pub = item.findtext('pubDate')
        if not pub:
            continue
        dt = parser.parse(pub)
        dt = dt.astimezone(ZoneInfo('Europe/Lisbon'))
        records.append((dt, item))

    records.sort(key=lambda x: x[0], reverse=True)
    return records[:n]


def main():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM noticias")
    conn.commit()

    latest = fetch_latest()
    for dt, item in latest:
        provedor  = 'Notícias ao Minuto'
        url        = item.findtext('link') or ''
        data_iso   = dt.isoformat()
        titulo     = item.findtext('title') or ''
        descricao  = item.findtext('description') or ''
        conteudo   = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or ''

        cur.execute(
            "INSERT INTO noticias (provedor, url, data, titulo, descricao, conteudo)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (provedor, url, data_iso, titulo, descricao, conteudo)
        )

    conn.commit()
    conn.close()
    print(f"{len(latest)} notícias inseridas na base de dados.")


if __name__ == '__main__':
    main()
