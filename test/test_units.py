import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

# --- SETUP IN-MEMORY DATABASE FOR TESTING ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- THE TESTS ---

def test_register_student():
    """Test 1: Successfully register a new student"""
    response = client.post(
        "/students/register",
        json={
            "username": "teststudent",
            "email": "student@example.com",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Student teststudent created"
    assert "id" in response.json()

def test_register_doctor():
    """Test 2: Successfully register a new doctor"""
    response = client.post(
        "/doctors/register",
        json={
            "username": "dr_smith",
            "password": "doctorpassword456",
            "contact": "123-456-7890",
            "price": 50.0
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Doctor dr_smith created"
    assert "id" in response.json()

def test_student_login():
    """Test 3: Register and then login a student"""
    # First, register the student
    client.post(
        "/students/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "mypassword"
        }
    )
    
    # Attempt login
    # Note: Your student login uses query parameters (username, password) 
    # based on the login_student signature in students.py
    response = client.post(
        "/students/login",
        params={"username": "loginuser", "password": "mypassword"}
    )
    
    assert response.status_code == 200
    assert response.json()["username"] == "loginuser"
    assert "id" in response.json()