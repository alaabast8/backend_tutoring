from fastapi import FastAPI
from .database import engine, Base
from .routes import doctors, students, ratings

# This command triggers the creation of tables in PostgreSQL
# It checks if they exist; if not, it creates them.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health API")

# Connect the files
app.include_router(doctors.router)
app.include_router(students.router)
app.include_router(ratings.router)

@app.get("/")
def read_root():
    return {"status": "System Online"}