from sqlalchemy import Column, Integer, String, Float
from database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    city = Column(String(255), index=True)
    age = Column(Integer, index=True)
    gender= Column(String(255), index=True)
    height = Column(Float, index=True)
    weight = Column(Float, index=True)
    bmi=Column(Float, index=True)
    verdict=Column(String(255), index=True)