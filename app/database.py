import os
import bcrypt  # Import bcrypt directly
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- REPLACED PASSLIB WITH DIRECT BCRYPT ---

def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    # 1. Convert string to bytes
    pwd_bytes = password.encode('utf-8')
    # 2. Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # 3. Return as string for database storage
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored hash.
    """
    # Convert both to bytes and verify
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

# --- DATABASE UTILS ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- TABLE MODELS ---

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True) # <--- Add this line
    hashed_password = Column(String)



class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    contact = Column(String)
    price_per_hour = Column(Float)

class StdDrRate(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    rating = Column(Integer)

from pydantic import BaseModel

class DoctorCreate(BaseModel):
    username: str
    password: str
    contact: str
    price: float

class LoginRequest(BaseModel):
    username: str
    password: str

from pydantic import BaseModel, EmailStr

class StudentCreate(BaseModel):
    username: str
    email: EmailStr
    password: str