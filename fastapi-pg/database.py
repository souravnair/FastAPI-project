from sqlalchemy import create_engine 
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os 

load_dotenv()

DATABASE_URL=os.environ.get("DB_URI", "")

engine=create_engine(url=DATABASE_URL, echo=True)
sessionLocal=sessionmaker(autoflush=False, bind=engine, autocommit=False)
Base=declarative_base()
