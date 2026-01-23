from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Doctor, get_password_hash

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/register")
def register_dr(username: str, password: str, contact: str, price: float, db: Session = Depends(get_db)):
    hashed = get_password_hash(password)
    new_dr = Doctor(username=username, hashed_password=hashed, contact=contact, price_per_hour=price)
    db.add(new_dr)
    db.commit()
    return {"message": f"Doctor {username} created"}