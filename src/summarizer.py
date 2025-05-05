#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import openai

from database import get_connection

# Configurações OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-3.5-turbo'


def init_summary_column(conn):
    """Adiciona coluna 'resumo' se não existir."""
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE noticias ADD COLUMN resumo TEXT;")
    except sqlite3.OperationalError:
        # coluna já existe
        pass
    conn.commit()


def fetch_unsummarized(conn):
    """Retorna lista de (id, titulo, descricao, conteudo) sem resumo."""
    cur = conn.cursor()
    cur.execute(
        "SELECT id, titulo, descricao, conteudo"
        " FROM noticias"
        " WHERE resumo IS NULL OR resumo = ''"
    )
    return cur.fetchall()


def generate_summary(titulo, descricao, conteudo):
    """Chama OpenAI ChatCompletion para gerar TLDR da notícia usando nova API."""
    messages = [
        {"role": "system", "content": "Você é um assistente que gera resumos TLDR de notícias."},
        {"role": "user", "content": (
            "Resuma a notícia abaixo em 1-2 frases no estilo TLDR, destacando apenas os pontos mais importantes.\n\n"
            f"Título: {titulo}\n"
            f"Descrição: {descricao}\n"
            f"Conteúdo: {conteudo}"
        )}
    ]
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=60,
        temperature=0.5
    )
    return resp.choices[0].message.content.strip()


def main():
    # Abre DB e garante coluna de resumo
    conn = get_connection()
    init_summary_column(conn)

    rows = fetch_unsummarized(conn)
    if not rows:
        print("Nenhuma notícia para resumir.")
        return

    cur = conn.cursor()
    for nid, titulo, descricao, conteudo in rows:
        try:
            resumo = generate_summary(titulo, descricao, conteudo)
            cur.execute(
                "UPDATE noticias SET resumo = ? WHERE id = ?",
                (resumo, nid)
            )
            conn.commit()
            print(f"Notícia {nid} resumida.")
        except Exception as e:
            print(f"Erro ao resumir notícia {nid}: {e}")

    conn.close()
    print(f"Resumidos {len(rows)} notícias.")

if __name__ == '__main__':
    main()
