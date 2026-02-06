from fastapi import FastAPI
#from database import engine, Base
#from routes import doctors, students, ratings ,studentInfo,doctorInfo,ml_predictions
from fastapi.middleware.cors import CORSMiddleware

# To this:
from app.database import engine, Base
from app.routes import doctors, students, ratings, studentInfo, doctorInfo, ml_predictions

# This command triggers the creation of tables in PostgreSQL
# It checks if they exist; if not, it creates them.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health API")
origins = ["*"]

# 2. Add the middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, etc.
    allow_headers=["*"], # Allows Content-Type, etc.
)

# Connect the files
app.include_router(doctors.router)
app.include_router(students.router)
app.include_router(ratings.router)
app.include_router(studentInfo.router)
app.include_router(doctorInfo.router)
app.include_router(ml_predictions.router) 
@app.get("/")
def read_root():
    return {"status": "System Online"}