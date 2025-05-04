import sqlite3
import database
import os

def test_init_and_tables(tmp_path, monkeypatch):
    dbf = tmp_path/'test.db'
    monkeypatch.setenv('DB_PATH', str(dbf))
    database.init_db()
    conn = sqlite3.connect(str(dbf))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    names = [r[0] for r in cur.fetchall()]
    assert 'articles' in names
    assert 'clusters' in names
    assert 'article_cluster' in names
    conn.close()
