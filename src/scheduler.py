from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
import os
from dotenv import load_dotenv
import scraper, clusterer, summarizer, emailer, database

load_dotenv()
database.init_db()
sched = BlockingScheduler(timezone='Europe/Lisbon')

def job():
    today = date.today().isoformat()
    new_ids = scraper.scrape()
    if not new_ids:
        return
    clusters = clusterer.cluster_by_date(today)
    summaries = summarizer.summarize_clusters(clusters)
    emailer.send_email(summaries)

sched.add_job(job, 'cron', hour=8, minute=0)
if __name__ == '__main__':
    sched.start()
