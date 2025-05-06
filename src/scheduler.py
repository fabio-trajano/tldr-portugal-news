#!/usr/bin/env python3
"""
Scheduler para executar automaticamente:
 1) Coleta das últimas notícias via scraper.py
 2) Geração de resumos via summarizer.py
 3) Envio de email via emailer.py
Todos os dias às 08:00 (horário de Lisboa).
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys

# Ajusta o path para importar os módulos locais
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import scraper
import summarizer
import emailer

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def job():
    logging.info("Iniciando tarefa diária de notícias")
    try:
        logging.info("-> Executando scraper")
        scraper.main()
        logging.info("-> Executando summarizer")
        summarizer.main()
        logging.info("-> Executando emailer")
        emailer.main()
        logging.info("Tarefa concluída com sucesso")
    except Exception as e:
        logging.error(f"Erro na tarefa diária: {e}", exc_info=True)

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone="Europe/Lisbon")
    scheduler.add_job(job, 'cron', hour=21, minute=59)
    logging.info("Scheduler iniciado. Próxima execução às 08:00 horário de Lisboa.")
    scheduler.start()
