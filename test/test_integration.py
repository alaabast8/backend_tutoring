import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# --- TEST SETUP ---
# Use an in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables BEFORE creating the test client
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    """Recreate tables before each test and drop them after."""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    # Create fresh tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)

# --- INTEGRATION TESTS ---

def test_doctor_registration_and_info_link():
    # 1. Register Doctor
    dr_reg = client.post("/doctors/register", json={
        "username": "dr_house",
        "password": "lupus_is_never_the_answer",
        "contact": "555-0199",
        "price": 150.0
    })
    dr_id = dr_reg.json()["id"]

    # 2. Add Doctor Info
    dr_info = {
        "doctor_id": dr_id,
        "uni_name": "Princeton-Plainsboro",
        "faculty": "Medicine",
        "department": "Diagnostics",
        "start_teaching_year": 2004
    }
    info_resp = client.post("/doctor-info/", json=dr_info)
    
    assert info_resp.status_code == 201
    assert info_resp.json()["data"]["department"] == "Diagnostics"



def test_student_registration_and_profile_creation():
    # 1. Register Student
    reg_resp = client.post("/students/register", json={
        "username": "student_flow",
        "email": "flow@test.com",
        "password": "password123"
    })
    student_id = reg_resp.json()["id"]

    # 2. Create Profile with NEW FIELDS
    profile_data = {
        "student_id": student_id,
        "first_name": "John",
        "last_name": "Doe",
        "uni_name": "Global Tech Uni",
        "faculty": "Engineering",
        "department": "CS",
        "major": "AI",
        "disability": False,
        "gpa": 3.8,
        "dob": "2002-05-15",
        "academic_year": 3,
        # NEW FIELDS ADDED HERE
        "athletic_status": "Non-Athlete",
        "country_of_origin": "Lebanon",
        "country_of_residence": "Lebanon",
        "gender": "Male",
        "primary_language": "Arabic",
        "study_hours": 15.5
    }
    
    prof_resp = client.post("/student-info/", json=profile_data) 
    
    assert prof_resp.status_code == 201 
    assert prof_resp.json()["data"]["first_name"] == "John"
    assert prof_resp.json()["data"]["gender"] == "Male"

def test_get_and_update_student_profile():
    # 1. Setup: Register and Create Profile
    reg_resp = client.post("/students/register", json={
        "username": "lifecycle_user",
        "email": "life@test.com",
        "password": "password123"
    })
    student_id = reg_resp.json()["id"]

    client.post("/student-info/", json={
        "student_id": student_id,
        "first_name": "Original",
        "last_name": "Name",
        "uni_name": "Test Uni",
        "faculty": "Science",
        "department": "Bio",
        "major": "Genetics",
        "gpa": 3.0,
        "dob": "2000-01-01",
        "academic_year": 1,
        # NEW FIELDS REQUIRED FOR CREATION
        "athletic_status": "Varsity",
        "country_of_origin": "France",
        "country_of_residence": "Lebanon",
        "gender": "Female",
        "primary_language": "French",
        "study_hours": 20.0
    })

    # 2. Test GET
    get_resp = client.get(f"/student-info/{student_id}")
    assert get_resp.status_code == 200

    # 3. Test PUT: Update new fields
    update_data = {
        "gpa": 3.9,
        "study_hours": 25.0,
        "country_of_residence": "UAE"
    }
    put_resp = client.put(f"/student-info/{student_id}", json=update_data)
    
    assert put_resp.status_code == 200
    assert put_resp.json()["data"]["study_hours"] == 25.0
    assert put_resp.json()["data"]["country_of_residence"] == "UAE"