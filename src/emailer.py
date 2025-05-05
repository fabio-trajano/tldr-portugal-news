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
from pathlib import Path

# Ajuste o import para o local correto do seu database.py
from database import DB_PATH

SMTP_HOST       = os.getenv('SMTP_HOST')
SMTP_PORT       = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER       = os.getenv('SMTP_USER')
SMTP_PASSWORD   = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS')  # vírgula-separados

def fetch_summaries():
    """Lê todas as notícias da base e retorna lista de dicts."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT titulo, url, resumo FROM noticias")
    rows = cur.fetchall()
    conn.close()

    summaries = []
    for titulo, url, resumo in rows:
        summaries.append({
            'titulo': titulo,
            'url': url,
            'resumo': resumo or ''
        })
    return summaries

async def _send(body: str) -> None:
    """
    Envia o e-mail montado em HTML para os destinatários via SMTP.
    """
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD and RECIPIENT_EMAILS):
        raise RuntimeError("Variáveis SMTP_HOST, SMTP_USER, SMTP_PASSWORD e RECIPIENT_EMAILS devem estar definidas no .env")

    to_addrs = [r.strip() for r in RECIPIENT_EMAILS.split(',') if r.strip()]

    msg = EmailMessage()
    msg['Subject'] = 'TLDR Notícias Portugal'
    msg['From']    = SMTP_USER
    msg['To']      = ", ".join(to_addrs)
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
    """
    Formata a lista de resumos em HTML e dispara o envio.
    """
    # Monta o corpo do e-mail em HTML
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

    # Envia de forma assíncrona
    asyncio.run(_send(body))

if __name__ == '__main__':
    summaries = fetch_summaries()
    if not summaries:
        print("Nenhuma notícia para enviar.")
    else:
        send_email(summaries)
        print(f"E-mail enviado a {RECIPIENT_EMAILS}.")
