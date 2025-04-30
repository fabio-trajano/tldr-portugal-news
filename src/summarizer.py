import os
import openai
import database

openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_clusters(clusters):
    results = []
    for lab, aids in clusters.items():
        articles = []
        for aid in aids:
            row = database.get_articles_by_date(
                __import__('datetime').date.today().isoformat()
            )
        # reconstruir lista de artigos do cluster
        arts = [a for a in database.get_articles_by_date(
                  __import__('datetime').date.today().isoformat()
               ) if a['id'] in aids]
        prompt = 'Resume em português estes artigos:\n\n'
        for a in arts[:5]:
            prompt += f"- {a['title']}: {a['content'][:500]}...\n"
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role':'user','content':prompt}]
        )
        summary = resp.choices[0].message.content.strip()
        cid = database.insert_cluster(summary)
        for aid in aids:
            database.map_article_to_cluster(aid, cid)
        results.append({'summary': summary, 'articles': arts})
    return results
