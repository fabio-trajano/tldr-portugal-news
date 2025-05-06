# TLDR Portugal News

A complete system to fetch news via RSS, generate TLDR summaries, send emails, and provide a RAG chatbot interface with Gradio.

---

## 📁 Project Structure

```
├── src/
│   ├── database.py      # Initializes SQLite database
│   ├── scraper.py       # Fetches RSS news and populates the DB
│   ├── summarizer.py    # Generates TLDR summaries with OpenAI
│   ├── emailer.py       # Sends email with summaries and links
│   ├── chatbot.py       # RAG chatbot using FAISS + Gradio
│   └── scheduler.py     # APScheduler automation script
├── .env                # Environment variables for API keys and SMTP
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🚀 Features

1. **database.py**: Creates `noticias.db` with table:

   * `id, provider, url, date, title, description, content, summary`

2. **scraper.py**: Fetches the **5** latest items from the "Última Hora" RSS feed of Notícias ao Minuto, clears old records, and inserts new ones.

3. **summarizer.py**: Reads entries without `summary`, calls OpenAI (`gpt-3.5-turbo`) to generate a 1–2 sentence TLDR, and updates the DB.

4. **emailer.py**: Formats an HTML email including:

   * Links to the chatbot (`http://localhost:7860`) and GitHub repository.
   * A list of titles as links + the summary text.
   * Sends via SMTP (configured in `.env`).

5. **chatbot.py**: A simple RAG chatbot with FAISS + Gradio:

   * Loads the **5** most recent articles (`content` field).
   * Indexes embeddings and launches a Gradio UI.
   * If asked "Which news?" it lists titles; for detailed queries it injects full article content.

6. **schedule.py**: Automates the full pipeline (scraper → summarizer → emailer). On startup it runs the entire pipeline immediately and then repeats hourly (Europe/Lisbon timezone). After initializing the database and testing each step, simply launch `scheduler.py` to keep summaries and emails up to date automatically immediately on start and then hourly:

   1. `scraper.main()`
   2. `summarizer.main()`
   3. `emailer.main()`

---

## ⚙️ Environment Variables (`.env`)

```ini
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# SMTP settings for email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_username
SMTP_PASSWORD=your_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
```

> **Note**: Do **not** commit your `.env` file to version control.

---

## 📦 Installation

1. Clone the repository:

```bash
git clone [https://github.com/fabio-trajano/tldr-portugal-news.git](https://github.com/fabio-trajano/tldr-portugal-news.git)
cd tldr-portugal-news
```

2. Create and activate a Python virtual environment:
```bash
python3 -m venv .venv       # create
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate   # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
````

4. Configure your `.env` with the required variables.

---

## 🏃‍♂️ Usage

### Initialize DB and Fetch News
```bash
python src/database.py   # Create the table
python src/scraper.py    # Insert 5 latest articles
````

### Generate Summaries

```bash
python src/summarizer.py
```

### Send Email Manually

```bash
python src/emailer.py
```

### Launch the Chatbot UI

```bash
python src/chatbot.py
# Open http://localhost:7860 in your browser
```

### OR Run Scheduler (Immediate + Hourly)
After initializing the database and verifying each component manually, automate the full pipeline with:

```bash
python src/scheduler.py
```
This will:

1. Execute scraper, summarizer, and emailer immediately.

2. Repeat those steps every hour.

Press Ctrl+C to stop the scheduler.
---


## 📄 License

This project is licensed under the [MIT License](LICENSE).
