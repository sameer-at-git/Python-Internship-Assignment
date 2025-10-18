# main.py (The RAG API)
import os
import re
import pandas as pd
from sqlalchemy import create_engine
from groq import Groq
from fastapi import FastAPI
from dotenv import load_dotenv
import re
from typing import List, Dict, Tuple

load_dotenv()

app = FastAPI(title="Phone Specs RAG API")

NEON_URL = os.getenv("NEON_DATABASE_URL")
GROQ_API_KEY = os.getenv("CHATGROQ_API_KEY")

if not NEON_URL:
    raise RuntimeError("FATAL: NEON_DATABASE_URL not set in .env")
if not GROQ_API_KEY:
    raise RuntimeError("FATAL: GROQ_API_KEY not set in .env")

engine = create_engine(NEON_URL)
groq_client = Groq(api_key=GROQ_API_KEY)

import re
from typing import List, Dict, Tuple

# Helper function to get all columns from the database (required for dynamic querying)
def get_all_db_columns(engine) -> List[str]:
    """Fetches all column names from the samsung_phones table."""
    try:
        query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'samsung_phones';"
        with engine.connect() as conn:
            # Fetch column names and return them as a list
            df = pd.read_sql_query(query, conn)
            # Filter out internal/system columns if any, and ensure correct case
            return [col for col in df['column_name'].tolist() if col not in ['index', 'id']]
    except Exception as e:
        print(f"Error fetching columns: {e}")
        # Return a sensible default based on your previous structure if fetch fails
        return ["Model", "Price", "Launch Announcement", "Display Size", "Memory Internal", "Ram", "Primary Camera", "Battery Capacity"]


# --- Dynamic Search Mapping ---
# Maps user-friendly search terms to the actual column names (case-sensitive)
COLUMN_MAP = {
    "display": "Display Size",
    "screen": "Display Size",
    "ram": "Ram",
    "memory": "Memory Internal",
    "storage": "Memory Internal",
    "camera": "Primary Camera",
    "photography": "Primary Camera",
    "battery": "Battery Capacity",
    "launch": "Launch Announcement",
    "price": "Price",
    "specs": None, # Special case for general specs
    "specifications": None,
}

# Pre-fetch columns once at startup (assuming 'engine' is initialized globally/before this call)
# NOTE: This line needs to be called AFTER your global 'engine' is defined.
# ALL_DB_COLUMNS = get_all_db_columns(engine) 
# For demonstration, we use the known columns from your output:
ALL_DB_COLUMNS = ["Model", "Price", "Launch Announcement", "Display Size", "Memory Internal", "Ram", "Primary Camera", "Battery Capacity"]


def extract_models(user_question: str) -> List[str]:
    """Extracts model names (SXX Ultra, FXX, MXX, AXX, etc.) from the question."""
    # Pattern to capture common Samsung model formats (Galaxy S23 Ultra, A54, M17 5G, F07)
    # This is broad to catch common structures: Letter(s) followed by number(s), optionally with spaces and 5G
    pattern = r'(\bGalaxy\s+[A-Z]\d+[\s\d]*[Gg]?)|\b(S\d+\s+Ultra)|(\b[A-Z]\d+\s*[\d]*\s*[Gg]?)'
    
    matches = re.findall(pattern, user_question, re.I)
    
    models = []
    for match_tuple in matches:
        # Matches are returned as tuples, we join the non-empty parts
        full_match = ' '.join(filter(None, match_tuple)).strip()
        if full_match:
            # We normalize by ensuring "Samsung Galaxy" prefix for better lookup
            if not full_match.lower().startswith("samsung"):
                 full_match = "Samsung " + full_match
            models.append(full_match)

    # Use set to remove duplicates, then convert back to list
    return list(set(models))


def extract_criteria(user_question: str) -> List[str]:
    """Extracts the specific criteria (column names) requested by the user."""
    question_lower = user_question.lower()
    criteria = []
    
    for term, col_name in COLUMN_MAP.items():
        if term in question_lower:
            # If col_name is None, it means the user asked for "specs" or "specifications"
            if col_name is None:
                # For "specs" queries, return all relevant columns (excluding internal/meta)
                # You might return a flag here if you want ALL columns in the final selection
                return ALL_DB_COLUMNS
            criteria.append(col_name)

    # Ensure "Model" and "Price" are always included for context
    if "Model" not in criteria:
        criteria.insert(0, "Model")
    if "Price" not in criteria:
        criteria.insert(1, "Price")
        
    return list(set(criteria))


def query_postgres(user_question: str) -> pd.DataFrame:
    """Retrieves structured data from the Neon DB based on the four user patterns."""
    user_question = user_question.lower()
    
    # --------------------------------------------------------------------------
    # PATTERN 4: Available models based on a criterion (e.g., "Best camera", "Phones with 8GB Ram")
    # --------------------------------------------------------------------------
    if any(term in user_question for term in ["best", "available", "list", "top"]) or "under" in user_question:
        
        # --- BEST BATTERY UNDER X (Existing Logic) ---
        if "best battery" in user_question and "under" in user_question:
            price_match = re.search(r'under\s*[\$a-z]*\s*(\d+)', user_question, re.I)
            price_limit = int(price_match.group(1)) if price_match else 1000
            
            # Use the robust price cleaning logic
            query = f"""
            SELECT 
                "Model", 
                "Battery Capacity", 
                "Price" 
            FROM samsung_phones
            WHERE 
                COALESCE(NULLIF(TRIM(REGEXP_REPLACE("Price", '[^0-9\.]', '', 'g')), '')::NUMERIC, 99999999) <= {price_limit}
            ORDER BY "Battery Capacity" DESC
            LIMIT 5;
            """
            with engine.connect() as conn:
                try:
                    return pd.read_sql_query(query, conn)
                except Exception as e:
                    print(f"SQL Execution Error on Best Battery query: {e}")
                    return pd.DataFrame()

        # --- BEST X (New General Best/Filter Logic) ---
        criteria_list = extract_criteria(user_question)
        if len(criteria_list) > 2 and criteria_list[2] in ["Ram", "Primary Camera", "Display Size"]: 
            # Look for the main criteria to sort by (e.g., Ram or Camera)
            order_by_col = criteria_list[2] 
            
            # Simple assumption: order by the value of the criteria column
            # NOTE: For columns like 'Ram', you might need more complex parsing 
            # (e.g., '8 GB' vs '4 GB'), but this is a good start.
            query = f"""
            SELECT "{order_by_col}", "Model", "Price" FROM samsung_phones
            ORDER BY "{order_by_col}" DESC
            LIMIT 5;
            """
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn)
        
        # Fallback for complex 'best' queries not matched
        return pd.DataFrame()

    # --------------------------------------------------------------------------
    # PATTERNS 1, 2, 3: Specific Model(s) Query
    # --------------------------------------------------------------------------
    
    models = extract_models(user_question)
    criteria = extract_criteria(user_question)

    if not models:
        # Handles queries where a model should have been found but wasn't (e.g. general questions)
        return pd.DataFrame()

    # Normalize models for SQL lookup
    norm_models = [f"'{m.replace(' ', '').lower()}'" for m in models]
    
    # Select columns: use ALL columns if criteria is ALL_DB_COLUMNS (for "specs/specifications" queries)
    # Otherwise, select only the columns requested
    select_cols = ", ".join([f'"{c}"' for c in criteria])
    if ALL_DB_COLUMNS == criteria:
         select_cols = "*" # Select all if the user asked for full specs
    
    # Construct the base WHERE clause for the models
    where_clause = f"REPLACE(LOWER(\"Model\"), ' ', '') IN ({','.join(norm_models)})"
    
    # Final Query
    query = f"""
    SELECT {select_cols} 
    FROM samsung_phones
    WHERE {where_clause};
    """
    
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    # The result may contain more columns than requested if select_cols was '*', 
    # but the LLM generation step handles filtering.
    return df


def generate_natural_response(question, structured_data):
    """Generates a human-like answer using Groq and the structured data."""
    df = structured_data.copy()
    
    lines = []
    for _, row in df.iterrows():
        parts = [f"{c}: {v}" for c, v in row.items() if pd.notna(v)]
        lines.append("; ".join(parts))
    context = "\n".join(lines)

    prompt = [
        {"role": "system", "content": "You are a helpful assistant that answers user questions using the provided data context. Be concise and conversational."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer clearly and naturally based ONLY on the context. If the context is insufficient, state that politely."}
    ]

    try:
        resp = groq_client.chat.completions.create(
            messages=prompt, 
            model="llama-3.3-70b-versatile"
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "An error occurred while generating the natural language response."


@app.post("/query-phone-specs")
def unified_response_endpoint(user_query: str):
    """
    Accepts a user query, retrieves specs from the database, and generates 
    a natural language response using a large language model.
    """
    specs_df = query_postgres(user_query)
    
    if specs_df.empty:
        return {"answer": "I couldn't find a matching phone model or perform the requested comparison/filter based on your query."}

    response_text = generate_natural_response(user_query, specs_df)
    
    return {
        "query": user_query,
        "data_retrieved": specs_df.to_dict(orient='records'),
        "answer": response_text
    }