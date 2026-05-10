from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(url=os.environ.get("DB_URI", ""), echo=True, isolation_level="AUTOCOMMIT")

with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE \"healthcare-db\""))

