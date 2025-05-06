#!/usr/bin/env python3
"""
Scheduler to automate:
 1) Fetch latest news via scraper.py
 2) Generate summaries via summarizer.py
 3) Send email via emailer.py
After each run, restart the Gradio chatbot server so it's always up-to-date.
Executes immediately on start, then every hour (Lisbon timezone).
"""
import logging
import os
import sys
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler

# Adjust path to import local modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import scraper
import summarizer
import emailer

# For managing chatbot process
global chatbot_proc
chatbot_proc = None

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def start_chatbot():
    """(Re)start the Gradio chatbot server in the background."""
    global chatbot_proc
    # terminate existing process if running
    if chatbot_proc and chatbot_proc.poll() is None:
        logging.info("Stopping existing chatbot process...")
        chatbot_proc.terminate()
    # launch new chatbot process
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'chatbot.py')]
    chatbot_proc = subprocess.Popen(cmd)
    logging.info("Chatbot server started.")


def job():
    logging.info("Starting scheduled pipeline")
    try:
        logging.info("-> Running scraper")
        scraper.main()
        logging.info("-> Running summarizer")
        summarizer.main()
        logging.info("-> Running emailer")
        emailer.main()
        logging.info("Pipeline completed successfully")
        # restart chatbot to refresh its context
        start_chatbot()
    except Exception as e:
        logging.error(f"Error in scheduled pipeline: {e}", exc_info=True)


if __name__ == '__main__':
    # Execute the pipeline once immediately
    logging.info("Running initial pipeline execution...")
    job()

    # Start chatbot server once
    logging.info("Starting chatbot server...")
    start_chatbot()

    # Schedule hourly thereafter
    scheduler = BlockingScheduler(timezone="Europe/Lisbon")
    scheduler.add_job(job, 'interval', hours=1)
    logging.info("Scheduler started; next run in 1 hour.")
    scheduler.start()
