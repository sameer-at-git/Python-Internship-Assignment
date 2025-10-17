# Configuration settings
BASE_URL = "https://www.gsmarena.com"
SAMSUNG_URL = f"{BASE_URL}/samsung-phones-9.php"
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries
MAX_PHONES = 30
LOG_LEVEL = "INFO"

# PostgreSQL configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "samsung_phones_db",
    "user": "your_username",
    "password": "your_password"
}

# RAG Module configuration
FUZZY_MATCH_THRESHOLD = 80
MAX_RESULTS = 10

# Ollama configuration
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model_name": "mistral",  # or "llama2", "codellama", etc.
    "temperature": 0.3,
    "max_tokens": 2000
}

# FastAPI configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True
}

# Admin configuration
ADMIN_KEY = "your_admin_password"  # Change this in production