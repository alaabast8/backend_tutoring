from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Doctor, get_password_hash, verify_password

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/register")
def register_dr(username: str, password: str, contact: str, price: float, db: Session = Depends(get_db)):
    # Check if doctor already exists
    existing_dr = db.query(Doctor).filter(Doctor.username == username).first()
    if existing_dr:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = get_password_hash(password)
    new_dr = Doctor(username=username, hashed_password=hashed, contact=contact, price_per_hour=price)
    db.add(new_dr)
    db.commit()
    db.refresh(new_dr)
    return {"message": f"Doctor {username} created", "id": new_dr.id}

@router.post("/login")
def login_dr(username: str, password: str, db: Session = Depends(get_db)):
    # 1. Find the doctor by username
    dr = db.query(Doctor).filter(Doctor.username == username).first()
    
    # 2. If dr doesn't exist or password doesn't match
    if not dr or not verify_password(password, dr.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return {"message": "Login successful", "doctor_id": dr.id, "username": dr.username}