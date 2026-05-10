from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import sessionLocal, engine
from models import Base, Patient
from crud import get_patient, create_patient

class PatientCreate(BaseModel):
    name: str
    city: str
    age: int
    gender: str
    height: float
    weight: float

# class Patient(BaseModel):
#     id: int
#     name: str
#     city: str
#     age: int
#     gender: str
#     height: float
#     weight: float
#     bmi: float
#     verdict: str
    
#     class Config:
#         from_attributes = True

app=FastAPI()

#Create tables in the database
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/patients", response_model=Patient)
async def create_patient_endpoint(patient: PatientCreate, db: Session = Depends(get_db)):
    return create_patient(db, patient)

@app.get("/patients/{p_id}", response_model=Patient)
async def get_patient_endpoint(p_id:int, db:Session=Depends(get_db)):
    patient=get_patient(db=db, p_id=p_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")    
    return patient

@app.put("/patients/{p_id}", response_model=Patient)
async def update_patient(p_id:int, update_patient:PatientCreate, db:Session=Depends(get_db)):
    patient_data=get_patient(db=db, p_id=p_id)
    if patient_data is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_data.name = update_patient.name
    patient_data.city = update_patient.city
    patient_data.age = update_patient.age
    patient_data.gender = update_patient.gender
    patient_data.height = update_patient.height
    patient_data.weight = update_patient.weight
    
    # Recalculate BMI
    patient_data.bmi = round(update_patient.weight / (update_patient.height ** 2), 2)
    
    # Recalculate verdict based on new BMI
    bmi = patient_data.bmi
    if bmi < 18.0:
        patient_data.verdict = "Underweight"
    elif bmi > 18 and bmi < 30:
        patient_data.verdict = "Normal"
    else:
        patient_data.verdict = "Obese"
    
    db.commit()
    db.refresh(patient_data)
    return patient_data

@app.delete("/patients/{p_id}")
async def delete_patient(p_id: int, db:Session=Depends(get_db)):
    patient_data=get_patient(db=db, p_id=p_id)
    if patient_data is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient_data)
    db.commit()

    return {"detail": "Patient deleted"}
