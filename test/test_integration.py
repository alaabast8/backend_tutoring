import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# --- TEST SETUP ---
# Use an in-memory database instead of a file////
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
        print("feifs")
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
    # 1. Register Student
    reg_resp = client.post("/students/register", json={
        "username": "student_flow",
        "email": "flow@test.com",
        "password": "password123"
    })
    student_id = reg_resp.json()["id"]

    # 2. Create Profile (Updated URL and logic)
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
    
    # FIX 1: URL changed to "/student-info"
    prof_resp = client.post("/student-info/", json=profile_data) 
    
    # FIX 3: Check for 201 instead of 200
    assert prof_resp.status_code == 201 
    
    # FIX 2: Access the "data" key
    assert prof_resp.json()["data"]["first_name"] == "John"

def test_doctor_registration_and_info_link():
    # 1. Register Doctor (This part is likely fine)
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
    # FIX: Use hyphenated URL
    info_resp = client.post("/doctor-info/", json=dr_info)
    
    # FIX: Expect 201, not 200
    assert info_resp.status_code == 201
    # FIX: Access the nested "data" dictionary
    assert info_resp.json()["data"]["department"] == "Diagnostics"

def test_get_and_update_student_profile():
    """
    Test 4: Retrieve and Update Flow
    Register -> Create Profile -> Get Profile -> Update Profile -> Verify Change.
    """
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
        "academic_year": 1
    })

    # 2. Test GET: Fetch the profile
    get_resp = client.get(f"/student-info/{student_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["first_name"] == "Original"

    # 3. Test PUT: Update the GPA and Academic Year
    update_data = {
        "gpa": 3.9,
        "academic_year": 2
    }
    put_resp = client.put(f"/student-info/{student_id}", json=update_data)
    
    assert put_resp.status_code == 200
    assert put_resp.json()["data"]["gpa"] == 3.9
    assert put_resp.json()["data"]["academic_year"] == 2