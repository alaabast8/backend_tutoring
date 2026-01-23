# app/routes/ratings.py
from fastapi import APIRouter

router = APIRouter(prefix="/ratings", tags=["Ratings"]) # Ensure this is 'router'

@router.post("/")
def create_rating():
    return {"message": "success"}