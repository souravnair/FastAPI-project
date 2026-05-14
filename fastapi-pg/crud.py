from sqlalchemy.orm import Session
# from typing import Any
from models import Patient
from schemas import PatientCreate

def get_patient(db:Session, p_id: int):
    return db.query(Patient).filter(Patient.id==p_id).first()

def create_patient(db:Session, patient_data:PatientCreate):
    # Calculate BMI from weight (kg) and height (m)
    bmi:float = patient_data.weight / (patient_data.height ** 2)
    
    # Calculate verdict based on BMI
    if bmi < 18.0:
        verdict = "Underweight"
    elif bmi > 18 and bmi < 30:
        verdict = "Normal"
    else:
        verdict = "Obese"
    
    patient = Patient(
        name=patient_data.name,
        city=patient_data.city,
        age=patient_data.age,
        gender=patient_data.gender,
        height=patient_data.height,
        weight=patient_data.weight,
        bmi=bmi,
        verdict=verdict
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient