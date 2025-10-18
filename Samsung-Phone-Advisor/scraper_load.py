# scraper_and_load.py (Run ONCE)
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

NEON_URL = os.getenv("NEON_DATABASE_URL")
if not NEON_URL:
    raise ValueError("NEON_DATABASE_URL not found in environment variables.")

engine = create_engine(NEON_URL)

table_name = "samsung_phones"
csv_file = "samsung_phones_specs.csv" 

try:
    df = pd.read_csv(csv_file)
    print(f"Data loaded from {csv_file}. {len(df)} rows found.")
except FileNotFoundError:
    print(f"Error: {csv_file} not found. Did you run the scraping code first?")
    exit()

try:
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"CSV successfully inserted into Neon PostgreSQL table '{table_name}'.")

    df_pg = pd.read_sql(f"SELECT COUNT(*) FROM {table_name};", engine)
    print(f"Database verification: {df_pg.iloc[0, 0]} rows in table.")

except Exception as e:
    print(f"Failed to connect or insert data to Neon DB. Check NEON_DATABASE_URL: {e}")

