import os
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE CONNECTION ---
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,pool_pre_ping=True,)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- PASSWORD SECURITY ---

def get_password_hash(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored hash."""
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

# --- SQLALCHEMY MODELS ---

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationship to the profile info
    profile = relationship("StudentInfo", back_populates="owner", uselist=False)

class StudentInfo(Base):
    __tablename__ = "students_info"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    first_name = Column(String)
    last_name = Column(String)
    uni_name = Column(String)
    faculty = Column(String)
    department = Column(String)
    major = Column(String)
    disability = Column(Boolean, default=False)
    gpa = Column(Float)
    dob = Column(String)  # Format: YYYY-MM-DD
    academic_year = Column(Integer)

    # Database level constraint for year 0-5
    __table_args__ = (
        CheckConstraint('academic_year >= 0 AND academic_year <= 5', name='year_range_check'),
    )

    owner = relationship("Student", back_populates="profile")

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

# --- PYDANTIC SCHEMAS (For API Validation) ---

# Student Schemas
class StudentCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Student Info Schemas
class StudentInfoBase(BaseModel):
    first_name: str
    last_name: str
    uni_name: str
    faculty: str
    department: str
    major: str
    disability: bool = False
    gpa: float
    dob: str
    academic_year: int

class StudentInfoCreate(StudentInfoBase):
    student_id: int

class StudentInfoUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    uni_name: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    disability: Optional[bool] = None
    gpa: Optional[float] = None
    dob: Optional[str] = None
    academic_year: Optional[int] = None

# Doctor Schemas
class DoctorCreate(BaseModel):
    username: str
    password: str
    contact: str
    price: float

class LoginRequest(BaseModel):
    username: str
    password: str