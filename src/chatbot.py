#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import numpy as np
import faiss
import openai
import gradio as gr

# Configura tua chave de API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Parâmetros
DB_PATH      = os.path.join(os.path.dirname(__file__), 'noticias.db')
EMB_MODEL    = 'text-embedding-ada-002'
CHAT_MODEL   = 'gpt-3.5-turbo'
NUM_ARTICLES = 5   # usa 5 notícias mais recentes
TOP_K        = 3   # número de artigos para contexto

def get_embedding(text: str) -> np.ndarray:
    resp = openai.embeddings.create(model=EMB_MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype='float32')

def load_articles():
    """Carrega as últimas notícias da base usando o campo 'conteudo'."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT titulo, descricao, conteudo, url FROM noticias ORDER BY data DESC LIMIT ?",
        (NUM_ARTICLES,)
    )
    rows = cur.fetchall()
    conn.close()

    texts, metas = [], []
    for titulo, descricao, conteudo, url in rows:
        txt = f"Título: {titulo}\nDescrição: {descricao}\nConteúdo completo: {conteudo}"
        texts.append(txt)
        metas.append({'titulo': titulo, 'url': url, 'conteudo': conteudo})

    embs = [get_embedding(t) for t in texts]
    embs = np.vstack(embs)
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    embs_norm = embs / norms

    dim = embs_norm.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs_norm)
    return metas, index

# carrega documentos uma vez
METAS, INDEX = load_articles()

def chat_fn(query, history):
    """Processa pergunta, busca notícias mais relacionadas e gera resposta contextualizada."""
    # embedding da pergunta
    q_emb = get_embedding(query)
    q_emb_norm = q_emb / np.linalg.norm(q_emb)
    _, I = INDEX.search(q_emb_norm.reshape(1, -1), TOP_K)

    # constrói contexto com conteúdo completo de cada artigo relevante
    context = ''
    for idx in I[0]:
        m = METAS[idx]
        context += (
            f"<h4><a href=\"{m['url']}\">{m['titulo']}</a></h4>"
            f"<p>{m['conteudo']}</p>"
        )
    context += '<hr>'

    # prompt do sistema
    system_prompt = (
        "Você é um assistente que responde com base em notícias completas recentes:\n"
        f"{context}"
        "Responda de forma objetiva citando detalhes precisos do conteúdo fornecido."
    )

    # monta mensagens para o Chat API
    messages = [{'role': 'system', 'content': system_prompt}]
    for msg in history:
        messages.append(msg)
    messages.append({'role': 'user', 'content': query})

    # chamada à nova API do OpenAI
    resp = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.2
    )
    ans = resp.choices[0].message.content

    # atualiza histórico
    history.append({'role': 'user', 'content': query})
    history.append({'role': 'assistant', 'content': ans})
    return history, history, ''

# interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 Chatbot TLDR Notícias Portugal")
    chatbot = gr.Chatbot(type='messages')
    state = gr.State([])
    txt = gr.Textbox(placeholder="Pergunte algo sobre as notícias...", label="Sua pergunta")
    txt.submit(
        chat_fn,
        inputs=[txt, state],
        outputs=[chatbot, state, txt]
    )

demo.launch(share=True)
