from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Student, get_password_hash, pwd_context

router = APIRouter(prefix="/students", tags=["Students"])

# 1. REGISTER
@router.post("/register")
def register_student(username: str, password: str, db: Session = Depends(get_db)):
    # Check if student already exists
    existing_user = db.query(Student).filter(Student.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = get_password_hash(password)
    new_std = Student(username=username, hashed_password=hashed)
    db.add(new_std)
    db.commit()
    db.refresh(new_std)
    return {"message": f"Student {username} created", "id": new_std.id}

# 2. LOGIN
@router.post("/login")
def login_student(username: str, password: str, db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(Student).filter(Student.username == username).first()
    
    # Check if user exists and password is correct
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return {"message": "Login successful", "username": user.username}