from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import asyncio
import ssl
import certifi
import aiosmtplib
from email.message import EmailMessage
from database import DB_PATH

to_addrs = [r.strip() for r in os.getenv('RECIPIENT_EMAILS', '').split(',') if r.strip()]
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

REPO_LINK = 'https://github.com/fabio-trajano/tldr-portugal-news'
CHAT_LINK = 'http://localhost:7860'


def fetch_summaries():
    """Lê as notícias com resumo da base e retorna lista de dicts."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT titulo, url, resumo FROM noticias")
    rows = cur.fetchall()
    conn.close()
    return [{'titulo': t, 'url': u, 'resumo': r or ''} for t, u, r in rows]

async def _send(body: str) -> None:
    """Envia o e-mail via SMTP usando TLS."""
    msg = EmailMessage()
    msg['Subject'] = 'TLDR Notícias Portugal'
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(to_addrs)
    msg.set_content(body, subtype='html')

    tls_context = ssl.create_default_context(cafile=certifi.where())
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
        tls_context=tls_context
    )


def send_email(summaries: list[dict]) -> None:
    """Formata o corpo do e-mail e dispara o envio."""
    html = [
        '<h1>TLDR Notícias Portugal</h1>',
        f'<p>Chatbot disponível em: <a href="{CHAT_LINK}">{CHAT_LINK}</a></p>',
        f'<p>Repositório: <a href="{REPO_LINK}">{REPO_LINK}</a></p>',
        '<ul>'
    ]
    for s in summaries:
        html.append(
            f'<li>'
            f'<a href="{s["url"]}">{s["titulo"]}</a><br>'
            f'{s["resumo"]}'
            f'</li>'
        )
    html.append('</ul>')
    body = '\n'.join(html)
    asyncio.run(_send(body))


def main():
    summaries = fetch_summaries()
    if not summaries:
        print('Nenhuma notícia para enviar.')
        return
    send_email(summaries)
    print(f'E-mail enviado para: {os.getenv("RECIPIENT_EMAILS")}')

if __name__ == '__main__':
    main()
