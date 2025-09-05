from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Create tables if they don’t exist
def init_db():
    print("Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)


# Dependencies for Fast API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()