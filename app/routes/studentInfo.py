from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Student, StudentInfo, StudentInfoCreate, StudentInfoUpdate

router = APIRouter(prefix="/student-info", tags=["Student Info"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_student_info(details: StudentInfoCreate, db: Session = Depends(get_db)):
    # Verify student exists
    student = db.query(Student).filter(Student.id == details.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student account not found")

    # Prevent duplicate profiles
    existing = db.query(StudentInfo).filter(StudentInfo.student_id == details.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists for this student")

    new_info = StudentInfo(**details.dict())
    db.add(new_info)
    db.commit()
    db.refresh(new_info)
    return {"message": "Profile created successfully", "data": new_info}

@router.get("/{student_id}")
def get_student_info(student_id: int, db: Session = Depends(get_db)):
    info = db.query(StudentInfo).filter(StudentInfo.student_id == student_id).first()
    if not info:
        raise HTTPException(status_code=404, detail="Profile not found")
    return info

@router.put("/{student_id}")
def update_student_info(student_id: int, updates: StudentInfoUpdate, db: Session = Depends(get_db)):
    db_info = db.query(StudentInfo).filter(StudentInfo.student_id == student_id).first()
    if not db_info:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update only fields provided in the request body
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_info, key, value)

    db.commit()
    db.refresh(db_info)
    return {"message": "Profile updated successfully", "data": db_info}

@router.get("/check/{student_id}")
def check_student_profile_exists(student_id: int, db: Session = Depends(get_db)):
    """
    Checks if a record exists in StudentInfo for a given student_id.
    """
    # We only need the ID to confirm existence, which is faster than fetching the whole row
    profile_exists = db.query(StudentInfo.id).filter(StudentInfo.student_id == student_id).first()
    
    if profile_exists:
        return {
            "exists": True, 
            "student_id": student_id, 
            "profile_id": profile_exists[0]
        }
    
    return {
        "exists": False, 
        "student_id": student_id, 
        "profile_id": None
    }