from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import database
from datetime import date

MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def cluster_by_date(date_str):
    arts = database.get_articles_by_date(date_str)
    if not arts:
        return {}
    texts = [a['content'] or a['title'] for a in arts]
    embs = MODEL.encode(texts)
    clustering = AgglomerativeClustering(
      n_clusters=None, distance_threshold=1.0
    ).fit(embs)
    labels = clustering.labels_
    clusters = {}
    for idx, lab in enumerate(labels):
        clusters.setdefault(lab, []).append(arts[idx]['id'])
    return clusters
