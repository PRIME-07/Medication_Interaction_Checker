import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "../req_10_sqlite_drugbank.db")  

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama URL
MODEL_NAME = "llama3.1:8b"  # Ollama model
