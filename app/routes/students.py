from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Student, get_password_hash

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/register")
def register_student(username: str, password: str, db: Session = Depends(get_db)):
    hashed = get_password_hash(password)
    new_std = Student(username=username, hashed_password=hashed)
    db.add(new_std)
    db.commit()
    return {"message": f"Student {username} created"}