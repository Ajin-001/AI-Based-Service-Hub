from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()
# Database credentials
DATABASE_URL = os.environ["DATABASE_URL"]

# SQLAlchemy engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Auth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)



