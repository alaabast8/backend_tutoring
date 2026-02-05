from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Doctor, get_password_hash, verify_password, DoctorCreate, LoginRequest

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/register")
def register_dr(details: DoctorCreate, db: Session = Depends(get_db)):
    # Check if doctor already existsfff
    existing_dr = db.query(Doctor).filter(Doctor.username == details.username).first()
    if existing_dr:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = get_password_hash(details.password)
    new_dr = Doctor(
        username=details.username, 
        hashed_password=hashed, 
        contact=details.contact, 
        price_per_hour=details.price
    )
    db.add(new_dr)
    db.commit()
    db.refresh(new_dr)
    return {"message": f"Doctor {details.username} created", "id": new_dr.id}

@router.post("/login")
def login_dr(credentials: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find the doctor by username
    dr = db.query(Doctor).filter(Doctor.username == credentials.username).first()
    
    # 2. Check password
    if not dr or not verify_password(credentials.password, dr.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return {"message": "Login successful", "doctor_id": dr.id, "username": dr.username}