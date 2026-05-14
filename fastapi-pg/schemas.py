from pydantic import BaseModel


class PatientCreate(BaseModel):
    # id:int
    name: str
    city: str
    age: int
    gender: str
    height: float
    weight: float


class PatientResponse(BaseModel):
    id: int
    name: str
    city: str
    age: int
    gender: str
    height: float
    weight: float
    bmi: float
    verdict: str

    class Config:
        from_attributes = True
