#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import asyncio
import ssl
import certifi
import aiosmtplib
from email.message import EmailMessage

# Ajuste o caminho para o seu database.py se necessário
from database import DB_PATH

SMTP_HOST        = os.getenv('SMTP_HOST')
SMTP_PORT        = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER        = os.getenv('SMTP_USER')
SMTP_PASSWORD    = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS')  # separados por vírgula

def fetch_summaries():
    """Lê todas as notícias com resumo da base e retorna lista de dicts."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT titulo, url, resumo FROM noticias")
    rows = cur.fetchall()
    conn.close()

    return [
        {'titulo': t, 'url': u, 'resumo': r or ''}
        for t, u, r in rows
    ]

async def _send(body: str) -> None:
    """Envia o e-mail com o conteúdo HTML via SMTP."""
    to_addrs = [r.strip() for r in RECIPIENT_EMAILS.split(',') if r.strip()]

    msg = EmailMessage()
    msg['Subject'] = 'TLDR Notícias Portugal'
    msg['From']    = SMTP_USER
    msg['To']      = ', '.join(to_addrs)
    msg.set_content(body, subtype='html')

    tls_context = ssl.create_default_context(cafile=certifi.where())

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
        tls_context=tls_context,
    )

def send_email(summaries: list[dict]) -> None:
    """Formata e dispara o envio de e-mail usando os resumos."""
    html = ["<h1>TLDR Notícias Portugal</h1>", "<ul>"]
    for s in summaries:
        html.append(
            f"<li>"
            f"<a href=\"{s['url']}\">{s['titulo']}</a><br>"
            f"{s['resumo']}"
            f"</li>"
        )
    html.append("</ul>")
    body = "\n".join(html)
    asyncio.run(_send(body))

def main():
    """Busca resumos e envia o e-mail."""
    summaries = fetch_summaries()
    if not summaries:
        print("Nenhuma notícia para enviar.")
    else:
        send_email(summaries)
        print(f"E-mail enviado para: {RECIPIENT_EMAILS}")

if __name__ == '__main__':
    main()
