# scripts/seed_db.py
from dotenv import load_dotenv
import database

load_dotenv()
database.init_db()
print('Base de dados inicializada em', __import__('os').getenv('DB_PATH', 'news.db'))
