import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

# IMPORTANT: Adjust these imports based on your actual project structure
# If your files are in the root, use: from database import Base, get_db
# If they're in an 'app' folder, use: from app.database import Base, get_db
from app.main import app
from app.database import Base, get_db

# --- TEST SETUP ---
# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Important for in-memory SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override the database dependency to use test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test and drop them after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- INTEGRATION TESTS ---

def test_student_registration_and_profile_creation():
    """Test 1: Student Registration and Profile Creation Flow"""
    # 1. Register Student
    reg_resp = client.post("/students/register", json={
        "username": "student_flow",
        "email": "flow@test.com",
        "password": "password123"
    })
    
    # Check registration succeeded
    assert reg_resp.status_code in [200, 201], f"Registration failed: {reg_resp.json()}"
    student_id = reg_resp.json()["id"]

    # 2. Create Profile
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
    
    prof_resp = client.post("/student-info/", json=profile_data)
    
    # Check profile creation succeeded
    assert prof_resp.status_code == 201, f"Profile creation failed: {prof_resp.json()}"
    
    # Handle different response structures
    response_data = prof_resp.json()
    if "data" in response_data:
        assert response_data["data"]["first_name"] == "John"
    else:
        assert response_data["first_name"] == "John"


def test_doctor_registration_and_info_link():
    """Test 2: Doctor Registration and Info Creation Flow"""
    # 1. Register Doctor
    dr_reg = client.post("/doctors/register", json={
        "username": "dr_house",
        "password": "lupus_is_never_the_answer",
        "contact": "555-0199",
        "price": 150.0
    })
    
    assert dr_reg.status_code in [200, 201], f"Doctor registration failed: {dr_reg.json()}"
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
    
    assert info_resp.status_code == 201, f"Doctor info creation failed: {info_resp.json()}"
    
    # Handle different response structures
    response_data = info_resp.json()
    if "data" in response_data:
        assert response_data["data"]["department"] == "Diagnostics"
    else:
        assert response_data["department"] == "Diagnostics"


def test_get_and_update_student_profile():
    """Test 3: Complete CRUD Flow - Register, Create, Read, Update, Verify"""
    # 1. Setup: Register Student
    reg_resp = client.post("/students/register", json={
        "username": "lifecycle_user",
        "email": "life@test.com",
        "password": "password123"
    })
    
    assert reg_resp.status_code in [200, 201]
    student_id = reg_resp.json()["id"]

    # 2. Create Profile
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

    # 3. Test GET: Fetch the profile
    get_resp = client.get(f"/student-info/{student_id}")
    assert get_resp.status_code == 200, f"Get profile failed: {get_resp.json()}"
    
    # Check first_name in response
    get_data = get_resp.json()
    first_name = get_data.get("first_name") or get_data.get("data", {}).get("first_name")
    assert first_name == "Original"

    # 4. Test PUT: Update the GPA and Academic Year
    update_data = {
        "gpa": 3.9,
        "academic_year": 2
    }
    put_resp = client.put(f"/student-info/{student_id}", json=update_data)
    
    assert put_resp.status_code == 200, f"Update failed: {put_resp.json()}"
    
    # Verify the update
    put_data = put_resp.json()
    if "data" in put_data:
        assert put_data["data"]["gpa"] == 3.9
        assert put_data["data"]["academic_year"] == 2
    else:
        assert put_data["gpa"] == 3.9
        assert put_data["academic_year"] == 2


def test_duplicate_student_registration():
    """Test 4: Ensure duplicate username/email is rejected"""
    # Register first student
    client.post("/students/register", json={
        "username": "duplicate_test",
        "email": "dup@test.com",
        "password": "password123"
    })
    
    # Try to register with same username
    dup_resp = client.post("/students/register", json={
        "username": "duplicate_test",
        "email": "different@test.com",
        "password": "password123"
    })
    
    # Should fail with 400 or 409
    assert dup_resp.status_code in [400, 409]


def test_student_login():
    """Test 5: Student Login Flow"""
    # 1. Register student
    client.post("/students/register", json={
        "username": "login_test",
        "email": "login@test.com",
        "password": "securepass"
    })
    
    # 2. Attempt login with correct credentials
    login_resp = client.post("/students/login", json={
        "username": "login_test",
        "password": "securepass"
    })
    
    assert login_resp.status_code == 200, f"Login failed: {login_resp.json()}"
    
    # 3. Attempt login with wrong password
    wrong_pass = client.post("/students/login", json={
        "username": "login_test",
        "password": "wrongpassword"
    })
    
    assert wrong_pass.status_code in [401, 403]


def test_academic_year_constraint():
    """Test 6: Verify academic_year constraint (0-5)"""
    # Register student
    reg_resp = client.post("/students/register", json={
        "username": "constraint_test",
        "email": "constraint@test.com",
        "password": "password123"
    })
    student_id = reg_resp.json()["id"]
    
    # Try to create profile with invalid academic year (> 5)
    invalid_profile = {
        "student_id": student_id,
        "first_name": "Test",
        "last_name": "User",
        "uni_name": "Test Uni",
        "faculty": "Engineering",
        "department": "CS",
        "major": "AI",
        "gpa": 3.5,
        "dob": "2000-01-01",
        "academic_year": 10  # Invalid: should be 0-5
    }
    
    invalid_resp = client.post("/student-info/", json=invalid_profile)
    
    # Should fail with 400 or 422
    assert invalid_resp.status_code in [400, 422]