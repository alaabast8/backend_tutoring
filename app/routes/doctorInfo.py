from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Doctor, DoctorInfo, DoctorInfoCreate, DoctorInfoUpdate

router = APIRouter(prefix="/doctor-info", tags=["Doctor Info"])

# 1. CHECK IF PROFILE EXISTS
@router.get("/check/{doctor_id}")
def check_doctor_profile(doctor_id: int, db: Session = Depends(get_db)):
    profile_exists = db.query(DoctorInfo.id).filter(DoctorInfo.doctor_id == doctor_id).first()
    print("hi")
    return {
        "exists": True if profile_exists else False,
        "doctor_id": doctor_id,
        "profile_id": profile_exists[0] if profile_exists else None
    }

# 2. CREATE PROFILE
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_doctor_info(details: DoctorInfoCreate, db: Session = Depends(get_db)):
    # Check if doctor exists in main table
    doctor = db.query(Doctor).filter(Doctor.id == details.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check for duplicates
    existing = db.query(DoctorInfo).filter(DoctorInfo.doctor_id == details.doctor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    new_info = DoctorInfo(**details.dict())
    db.add(new_info)
    db.commit()
    db.refresh(new_info)
    return {"message": "Doctor profile created", "data": new_info}

# 3. GET PROFILE
@router.get("/{doctor_id}")
def get_doctor_info(doctor_id: int, db: Session = Depends(get_db)):
    info = db.query(DoctorInfo).filter(DoctorInfo.doctor_id == doctor_id).first()
    if not info:
        raise HTTPException(status_code=404, detail="Profile not found")
    return info

# 4. UPDATE PROFILE
@router.put("/{doctor_id}")
def update_doctor_info(doctor_id: int, updates: DoctorInfoUpdate, db: Session = Depends(get_db)):
    db_info = db.query(DoctorInfo).filter(DoctorInfo.doctor_id == doctor_id).first()
    if not db_info:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_info, key, value)

    db.commit()
    db.refresh(db_info)
    return {"message": "Doctor profile updated", "data": db_info}