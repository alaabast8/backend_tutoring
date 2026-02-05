from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..database import StudentInfo,StudentGPA,StudentGPACreate
import os
import requests

router = APIRouter(prefix="/ml", tags=["ML Predictions"])

# ML Container URL (change based on environment)
ML_CONTAINER_URL = os.getenv("ML_CONTAINER_URL")

@router.post("/predict-gpa/{student_id}")
async def predict_student_gpa(student_id: int, db: Session = Depends(get_db)):
    """
    Fetch student data and get GPA prediction from ML container
    """
    # Get student info from database
    student = db.query(StudentInfo).filter(StudentInfo.student_id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Prepare data for ML container with defaults for missing values
    ml_input = {
        "student_id": student.student_id,  # For tracking only, not a feature
        "uni_name": student.uni_name or "Unknown",
        "major": student.major or "Unknown",
        "disability": student.disability if student.disability is not None else False,
        "dob": student.dob or "2000-01-01",
        "academic_year": student.academic_year if student.academic_year is not None else 1,
        "study_hours": student.study_hours if student.study_hours is not None else 0.0,
        "athletic_status": student.athletic_status or "Inactive",
        "country_of_origin": student.country_of_origin or "Unknown",
        "country_of_residence": student.country_of_residence or "Unknown",
        "primary_language": student.primary_language or "Unknown",
        "gender": student.gender or "Unknown",
        "dropout": False  # Default to False (student is not a dropout)
    }
    
    # try:
    #     # Call ML container
    #     response = requests.post(f"{ML_CONTAINER_URL}/predict", json=ml_input, timeout=10)
    #     response.raise_for_status()
        
    #     prediction = response.json()
    #     return prediction
    try:
        # Call ML container
        response = requests.post(f"{ML_CONTAINER_URL}/predict", json=ml_input, timeout=10)
        response.raise_for_status()
        
        prediction = response.json()
        predicted_gpa = prediction.get("predicted_gpa")  # Adjust based on your ML response format
        
        # Save or update GPA in database
        existing_gpa = db.query(StudentGPA).filter(StudentGPA.student_id == student_id).first()
        
        if existing_gpa:
            # Update existing record
            existing_gpa.predicted_gpa = predicted_gpa
        else:
            # Create new record
            new_gpa = StudentGPA(student_id=student_id, predicted_gpa=predicted_gpa)
            db.add(new_gpa)
        
        db.commit()
        
        return prediction
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503, 
            detail=f"ML service unavailable: {str(e)}"
        )