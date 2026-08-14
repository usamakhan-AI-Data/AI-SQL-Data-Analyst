# 🤖 AI SQL Data Analyst

Ask questions about your database in plain English and get instant, accurate answers — no SQL required.

**AI SQL Data Analyst** is a natural-language-to-SQL pipeline that inspects your database schema, generates a valid SQL query using an LLM, executes it safely, and returns the result through a clean, interactive Streamlit dashboard.

---

## ✨ Features

- **Natural language → SQL**: Ask questions like *"Top 5 customers by spending"* and get a correct, schema-aware SQL query.
- **Automatic schema extraction**: Reads your database's tables and columns at runtime via SQLAlchemy — no manual schema definitions to maintain.
- **LLM-powered query generation**: Uses Google's Gemini (`gemini-2.5-flash`) through LangChain to translate intent into SQL.
- **Safe output parsing**: Strips markdown code fences and reasoning artifacts from LLM output before execution.
- **Interactive dashboard**: A dark, modern Streamlit UI with query history, example prompts, step-by-step execution status, and downloadable CSV results.
- **Database-agnostic core**: Built on SQLAlchemy, so the schema extraction layer works with SQLite, PostgreSQL, MySQL, and more with minimal changes.

---

## 🏗️ Architecture

```
User question
     │
     ▼
┌─────────────────┐
│  Schema Extractor │  → Inspects DB via SQLAlchemy, builds JSON schema
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Text-to-SQL LLM  │  → Gemini (via LangChain) generates SQL from schema + question
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Output Cleaner   │  → Strips markdown fences / reasoning tags
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  SQL Executor      │  → Runs query against the database
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Streamlit UI       │  → Displays results, SQL, and metrics
└─────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Orchestration | LangChain |
| Database toolkit | SQLAlchemy |
| Database | SQLite (default), extensible to Postgres/MySQL |
| Frontend | Streamlit |
| Data handling | Pandas |
| Env management | python-dotenv |
| Package manager | uv |

---

## 📁 Project Structure

```
AI-SQL-Data-Analyst/
├── main.py              # Schema extraction + text-to-SQL + query execution
├── forntend.py                # Streamlit frontend
├── database.db            # SQLite database (sample/local data)
├── .env                   # API keys (not committed)
├── requirements.txt        # or pyproject.toml if using uv
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A [Google AI Studio API key](https://aistudio.google.com/app/apikey) for Gemini

### Installation

```bash
git clone https://github.com/usamakhan-AI-Data/AI-SQL-Data-Analyst.git
cd AI-SQL-Data-Analyst

# using uv
uv sync

# or using pip
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Run the app

```bash
uv run streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`).

---

## 💬 Usage

1. Enter a question in plain English, e.g.:
   - *"Total products sold in 2025"*
   - *"Top 5 customers by spending"*
   - *"Which category sells the most?"*
2. Click **Analyze**.
3. View the generated result, inspect the underlying SQL query, and download results as CSV.

---

## 🗺️ Roadmap

- [ ] Support for PostgreSQL / MySQL connection strings via UI
- [ ] Query validation layer (guard against destructive statements)
- [ ] Multi-turn conversational context (follow-up questions)
- [ ] Chart/visualization generation from result sets
- [ ] Docker deployment support

---

## ⚠️ Notes on Safety

This project executes LLM-generated SQL directly against a live database. For production use, restrict the database user to **read-only** permissions and add query validation (e.g., blocking `DROP`, `DELETE`, `UPDATE`, `ALTER`) before execution.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Usama Khan** — AI Automation Specialist & Developer, [Neo Data AI](https://github.com/usamakhan-AI-Data)
