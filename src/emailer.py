import os
import asyncio
import ssl
import certifi
import aiosmtplib
from email.message import EmailMessage

async def _send(body: str) -> None:
    """
    Envia o e-mail com o conteúdo especificado usando SMTP.
    """
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASSWORD')
    to = os.getenv('RECIPIENT_EMAIL')

    msg = EmailMessage()
    msg['From'] = user
    msg['To'] = to
    msg['Subject'] = 'News Digest PT — Resumos diários'
    msg.set_content(body)

    # Cria contexto SSL usando o bundle do certifi para validação de certificados
    tls_context = ssl.create_default_context(cafile=certifi.where())

    await aiosmtplib.send(
        msg,
        hostname=host,
        port=port,
        username=user,
        password=pwd,
        start_tls=True,
        tls_context=tls_context,
    )

def send_email(summaries: list[dict]) -> None:
    """
    Formata os resumos e dispara o envio.
    summaries: lista de dicionários com 'summary' e 'articles'.
    """
    body = ''
    for c in summaries:
        body += f"RESUMO:\n{c['summary']}\n\nLinks:\n"
        for a in c['articles']:
            body += f"- {a['url']}\n"
        body += '\n' + ('-' * 40) + '\n\n'

    # Executa o envio de forma síncrona
    asyncio.run(_send(body))
