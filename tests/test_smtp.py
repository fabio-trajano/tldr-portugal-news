import os
import ssl
import certifi
import sys
import asyncio
from pathlib import Path
from email.message import EmailMessage
import aiosmtplib
from dotenv import load_dotenv

# 1) garante que o src/ está no PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

# 2) carrega o .env da raiz
load_dotenv(dotenv_path=str(ROOT / '.env'))

def build_message():
    msg = EmailMessage()
    msg['From']    = os.getenv('SMTP_USER')
    msg['To']      = os.getenv('RECIPIENT_EMAIL')
    msg['Subject'] = 'Teste SMTP integrado'
    msg.set_content('Se recebeste isto, funcionou!')
    return msg

async def send():
    # opcional: usa certifi para TLS caso seja necessário
    tls_context = ssl.create_default_context(cafile=certifi.where())
    await aiosmtplib.send(
        build_message(),
        hostname=os.getenv('SMTP_HOST'),
        port=int(os.getenv('SMTP_PORT')),
        username=os.getenv('SMTP_USER'),
        password=os.getenv('SMTP_PASSWORD'),
        start_tls=True,
        tls_context=tls_context,
    )

def test_smtp_send():
    # executa o envio; se lançar exceção, o pytest vai falhar o teste
    asyncio.run(send())
