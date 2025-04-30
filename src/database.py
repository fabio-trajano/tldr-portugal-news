import sqlite3
from datetime import datetime, timedelta

def get_conn():
    conn = sqlite3.connect(
        __import__('os').getenv('DB_PATH', 'news.db'),
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
      id INTEGER PRIMARY KEY,
      title TEXT,
      url TEXT UNIQUE,
      content TEXT,
      published TEXT,
      fetched_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clusters (
      id INTEGER PRIMARY KEY,
      summary TEXT,
      created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS article_cluster (
      article_id INTEGER,
      cluster_id INTEGER,
      PRIMARY KEY(article_id, cluster_id)
    )""")
    conn.commit()
    conn.close()

def insert_article(title, url, content, published):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        cur.execute(
          "INSERT INTO articles(title,url,content,published,fetched_at) VALUES(?,?,?,?,?)",
          (title, url, content, published, now)
        )
        conn.commit()
        aid = cur.lastrowid
    except sqlite3.IntegrityError:
        aid = None
    conn.close()
    return aid

def get_articles_by_date(date_str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
      "SELECT * FROM articles WHERE DATE(fetched_at)=?",
      (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_cluster(summary):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
      "INSERT INTO clusters(summary,created_at) VALUES(?,?)",
      (summary, now)
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def map_article_to_cluster(article_id, cluster_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
      "INSERT OR IGNORE INTO article_cluster(article_id,cluster_id) VALUES(?,?)",
      (article_id, cluster_id)
    )
    conn.commit()
    conn.close()

def get_clusters_last_days(days):
    conn = get_conn()
    cur = conn.cursor()
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    cur.execute("""
      SELECT c.id, c.summary, a.title, a.url
      FROM clusters c
      JOIN article_cluster ac ON c.id=ac.cluster_id
      JOIN articles a ON ac.article_id=a.id
      WHERE c.created_at>=?
      ORDER BY c.id
    """, (cutoff,))
    rows = cur.fetchall()
    conn.close()
    clusters = {}
    for r in rows:
        cid = r['id']
        clusters.setdefault(cid, {
            'summary': r['summary'],
            'articles': []
        })['articles'].append({
            'title': r['title'],
            'url': r['url']
        })
    return list(clusters.values())
