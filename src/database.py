import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'noticias.db'

def get_connection():
    """Abre ligação SQLite simples."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Cria tabela de notícias se não existir, incluindo URL e resumo."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
CREATE TABLE IF NOT EXISTS noticias (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    provedor   TEXT    NOT NULL,
    url        TEXT    NOT NULL,
    data       TEXT    NOT NULL,
    titulo     TEXT,
    descricao  TEXT,
    conteudo   TEXT,
    resumo     TEXT
)
""")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Base de dados inicializada em: {DB_PATH}")
