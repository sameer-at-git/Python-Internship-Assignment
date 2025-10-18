from typing import Optional
import re
import pandas as pd
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from groq import Groq

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    CHATGROQ_API_KEY: str = Field(..., env="CHATGROQ_API_KEY")
    GROQ_MODEL: str = Field("llama-3.3-70b-versatile", env="GROQ_MODEL")
    class Config:
        env_file = ".env"

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
client = Groq(api_key=settings.CHATGROQ_API_KEY)
app = FastAPI()

class QuestionIn(BaseModel):
    question: str

class AnswerOut(BaseModel):
    answer: str

keywords = ["display", "battery", "camera", "ram", "price", "launch", "memory"]

def _extract_model(user_question: str) -> Optional[str]:
    match = re.search(r'samsung galaxy\s+([a-z0-9\s\-]+)', user_question, re.I)
    if not match:
        return None
    phone_model = match.group(1).strip()
    phone_norm = ("Samsung Galaxy " + phone_model).replace(" ", "").lower()
    return phone_norm

def query_postgres(user_question: str) -> pd.DataFrame:
    search_terms = [k for k in keywords if k in user_question.lower()]
    phone_norm = _extract_model(user_question)
    if not phone_norm:
        return pd.DataFrame()
    phone = f"%{phone_norm}%"
    query = text('''
        SELECT * FROM samsung_phones
        WHERE REPLACE(LOWER("Model"), ' ', '') LIKE :phone
    ''')
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"phone": phone})
    if not df.empty and search_terms:
        cols = [c for c in df.columns if any(t in c.lower() for t in search_terms)] + ["Model"]
        cols = [c for c in cols if c in df.columns]
        df = df[cols]
    return df

def generate_natural_response(question: str, structured_data: pd.DataFrame):
    df = structured_data.copy()
    if df.shape[0] > 3:
        df = df.head(3)
    lines = []
    for _, row in df.iterrows():
        parts = [f"{c}: {v}" for c, v in row.items()]
        lines.append("; ".join(parts))
    context = "\n".join(lines)
    prompt = [
        {"role": "system", "content": "You are a helpful assistant that answers user questions using only the provided data context. If the answer cannot be determined from the context, say you don't know."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer clearly and naturally."}
    ]
    resp = client.chat.completions.create(messages=prompt, model=settings.GROQ_MODEL)
    return resp.choices[0].message.content.strip()

def unified_response(user_query: str) -> str:
    df = query_postgres(user_query)
    if df.empty:
        return "No matching phone found in database."
    return generate_natural_response(user_query, df)

@app.post("/ask", response_model=AnswerOut)
def ask(q: QuestionIn):
    question = q.question.strip() if q.question else ""
    if not question:
        raise HTTPException(status_code=422, detail="question is required")
    try:
        resp = unified_response(question)
        return AnswerOut(answer=resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
