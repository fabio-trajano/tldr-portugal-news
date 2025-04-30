from fastapi import FastAPI, Query
from pydantic import BaseModel
import database
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

class Article(BaseModel):
    title: str
    url: str

class Cluster(BaseModel):
    summary: str
    articles: list[Article]

@app.get('/clusters', response_model=list[Cluster])
def get_clusters(days: int = Query(7, ge=1, le=30)):
    return database.get_clusters_last_days(days)

@app.get('/query', response_model=Cluster)
def query(q: str, days: int = Query(7, ge=1, le=30)):
    clusters = database.get_clusters_last_days(days)
    summaries = [c['summary'] for c in clusters]
    emb_s = MODEL.encode(summaries)
    emb_q = MODEL.encode([q])[0]
    sims = np.dot(emb_s, emb_q) / (
      np.linalg.norm(emb_s, axis=1) * np.linalg.norm(emb_q)
    )
    idx = int(np.argmax(sims))
    return clusters[idx]
