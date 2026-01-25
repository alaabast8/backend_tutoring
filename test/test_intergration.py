import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , StaticPool
from app.main import app
from app.database import Base, get_db

# --- TEST SETUP ---
# Use an in-memory database instead of a file
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
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- INTEGRATION TESTS ---

def test_student_registration_and_profile_creation():
    """
    Test 1: Full Student Flow
    Register a student -> Use the returned ID to create their StudentInfo profile.
    """
    # 1. Register Student
    reg_resp = client.post("/students/register", json={
        "username": "student_flow",
        "email": "flow@test.com",
        "password": "password123"
    })
    student_id = reg_resp.json()["id"]

    # 2. Create Profile linked to that ID
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
        "academic_year": 3
    }
    # Note: Ensure your studentInfo.router is registered in main.py
    prof_resp = client.post("/studentInfo/", json=profile_data)
    
    assert prof_resp.status_code == 200
    assert prof_resp.json()["first_name"] == "John"

def test_doctor_registration_and_info_link():
    """
    Test 2: Full Doctor Flow
    Register a doctor -> Add professional DoctorInfo -> Verify link.
    """
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
    info_resp = client.post("/doctorInfo/", json=dr_info)
    
    assert info_resp.status_code == 200
    assert info_resp.json()["department"] == "Diagnostics"

def test_rating_system_linkage():
    """
    Test 3: Cross-Table interaction
    Register Student + Doctor -> Student leaves a rating for the Doctor.
    """
    # 1. Setup Student
    s_resp = client.post("/students/register", json={"username":"s1", "email":"s1@t.com", "password":"p"})
    sid = s_resp.json()["id"]
    
    # 2. Setup Doctor
    d_resp = client.post("/doctors/register", json={"username":"d1", "contact":"123", "price":10, "password":"p"})
    did = d_resp.json()["id"]

    # 3. Post Rating
    rating_data = {
        "student_id": sid,
        "doctor_id": did,
        "rating": 5
    }
    rate_resp = client.post("/ratings/", json=rating_data)
    
    assert rate_resp.status_code == 200
    assert rate_resp.json()["rating"] == 5