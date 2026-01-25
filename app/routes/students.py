from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Student, get_password_hash, verify_password

router = APIRouter(prefix="/students", tags=["Students"])

# 1. REGISTER
from ..database import get_db, Student, get_password_hash, verify_password, StudentCreate

@router.post("/register")
def register_student(details: StudentCreate, db: Session = Depends(get_db)):
    # 1. Check if username OR email already exists
    print("me test")
    existing_user = db.query(Student).filter(
        (Student.username == details.username) | (Student.email == details.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    hashed = get_password_hash(details.password)
    
    # 2. Add email to the new student object
    new_std = Student(
        username=details.username, 
        email=details.email, 
        hashed_password=hashed
    )
    
    db.add(new_std)
    db.commit()
    db.refresh(new_std)
    return {"message": f"Student {details.username} created", "id": new_std.id}

# 2. LOGIN
@router.post("/login")
def login_student(username: str, password: str, db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(Student).filter(Student.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # ADD THE ID HERE
    return {
        "message": "Login successful", 
        "username": user.username,
        "id": user.id  # <--- THIS IS CRUCIAL
    }