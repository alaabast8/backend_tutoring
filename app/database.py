import os
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from pydantic import BaseModel, EmailStr
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE CONNECTION ---
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- MODERN DECLARATIVE BASE ---
class Base(DeclarativeBase):
    pass

# --- PASSWORD SECURITY ---
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
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
    dob = Column(String)  # Format: YYYY-MM-DD
    academic_year = Column(Integer)
    
    # New Fields
    disability = Column(Boolean, default=False)
    athletic_status = Column(String) 
    country_of_origin = Column(String)
    country_of_residence = Column(String)
    gender = Column(String)
    primary_language = Column(String)
    study_hours = Column(Float)

    __table_args__ = (
        CheckConstraint('academic_year >= 0 AND academic_year <= 5', name='year_range_check'),
        {'extend_existing': True} # Prevents crash on redefinition
    )

    owner = relationship("Student", back_populates="profile")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    contact = Column(String)
    price_per_hour = Column(Float)

    profile = relationship("DoctorInfo", back_populates="owner", uselist=False)

class DoctorInfo(Base):
    __tablename__ = "doctor_info"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), unique=True)
    uni_name = Column(String)
    faculty = Column(String)
    department = Column(String)
    start_teaching_year = Column(Integer)

    owner = relationship("Doctor", back_populates="profile")

class StdDrRate(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    rating = Column(Integer)

class StudentGPA(Base):
    __tablename__ = "student_gpa"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    predicted_gpa = Column(Float)

# --- PYDANTIC SCHEMAS ---

class StudentCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class StudentInfoBase(BaseModel):
    first_name: str
    last_name: str
    uni_name: str
    faculty: str
    department: str
    major: str
    dob: str
    academic_year: int
    disability: bool = False
    athletic_status: str
    country_of_origin: str
    country_of_residence: str
    gender: str
    primary_language: str
    study_hours: float

class StudentInfoCreate(StudentInfoBase):
    student_id: int

class StudentInfoUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    uni_name: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    dob: Optional[str] = None
    academic_year: Optional[int] = None
    disability: Optional[bool] = None
    athletic_status: Optional[str] = None
    country_of_origin: Optional[str] = None
    country_of_residence: Optional[str] = None
    gender: Optional[str] = None
    primary_language: Optional[str] = None
    study_hours: Optional[float] = None

class DoctorCreate(BaseModel):
    username: str
    password: str
    contact: str
    price: float

class DoctorInfoBase(BaseModel):
    uni_name: str
    faculty: str
    department: str
    start_teaching_year: int

class DoctorInfoCreate(DoctorInfoBase):
    doctor_id: int

class DoctorInfoUpdate(BaseModel):
    uni_name: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    start_teaching_year: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class StudentGPACreate(BaseModel):
    student_id: int
    predicted_gpa: float

class StudentGPAResponse(BaseModel):
    id: int
    student_id: int
    predicted_gpa: float
    
    class Config:
        from_attributes = True  # For Pydantic v2, use orm_mode = True for Pydantic v1

class StudentGPAUpdate(BaseModel):
    predicted_gpa: float