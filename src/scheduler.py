"""
Scheduler para executar automaticamente:
 1) Coleta das últimas notícias via scraper.py
 2) Geração de resumos via summarizer.py
 3) Envio de email via emailer.py
Executa imediatamente ao iniciar e depois a cada hora (horário de Lisboa).
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import scraper
import summarizer
import emailer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def job():
    logging.info("Iniciando tarefa de notícias")
    try:
        logging.info("-> Executando scraper")
        scraper.main()
        logging.info("-> Executando summarizer")
        summarizer.main()
        logging.info("-> Executando emailer")
        emailer.main()
        logging.info("Tarefa concluída com sucesso")
    except Exception as e:
        logging.error(f"Erro na tarefa: {e}", exc_info=True)

if __name__ == '__main__':
    job()

    scheduler = BlockingScheduler(timezone="Europe/Lisbon")
    scheduler.add_job(job, 'interval', hours=1)
    logging.info("Scheduler iniciado. Próxima execução em 1 hora.")
    scheduler.start()
