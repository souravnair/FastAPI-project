from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse,Response
from pydantic import BaseModel, Field, computed_field
from typing import Annotated,Literal,Optional
import json
from typing import Any
import uvicorn

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(description="Patient ID", min_length=1,max_length=30,examples=["P001"])]
    name:Annotated[str, Field(description="Name of the patient")]
    city: Annotated[str, Field(description="City name")]
    age: Annotated[int, Field(description="Age of the patient", gt=0)]
    gender: Annotated[Literal["Male","Female","Others"], Field(description="Gender of the patient")]
    height: Annotated[float, Field(description="Height of the patient in mtrs")]
    weight: Annotated[float, Field(description="Weight of the patient in kgs")]
    # compute the BMI using a computed field
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    @computed_field
    def verdict(self) -> str:
        if self.bmi<18.0:
            return "Underweight"
        elif self.bmi>18 and self.bmi<30:
            return "Normal"
        else:
            return "Obese"

class UpdatePatient(BaseModel): #not taking id here cause it is provided by the user as path param
    name:Annotated[Optional[str], Field(None,description="Name of the patient")]
    city: Annotated[Optional[str], Field(None,description="City name")]
    age: Annotated[Optional[int], Field(None,description="Age of the patient", gt=0)]
    gender: Annotated[Optional[Literal["Male","Female","Others"]], Field(None,description="Gender of the patient")]
    height: Annotated[Optional[float], Field(None,description="Height of the patient in mtrs")]
    weight: Annotated[Optional[float], Field(None,description="Weight of the patient in kgs")]

def load_patients_data() -> dict[str, dict[str, Any]]:
    with open("patients.json", "r", encoding="utf-8") as p:
        patients_data: dict[str, dict[str, Any]] = json.load(p) #if file is open use json.load(file) ==> json.load(p) instead of loading the file separately and loading the string using json.loads()
        # print(patients_data)
        p.close()
    return patients_data

def write_patients_data(data:dict["str", dict["str","str"]])->bool:
    with open("patients.json", "w", encoding="utf-8")  as p:
        json.dump(data,p)
        p.close()
    return True


@app.get("/")
def main():
    return {"message": "Welcome to patients server"}

# @app.get("/patients")
# def view_patients():
#     result=load_patients_data()
#     return {"result": result}

@app.get("/patients/{pid}")
def get_patient_data(pid:str=Path(title="patient id",description="Returns the patient details for the given PID",examples=["P001"],max_length=4)):
    data=load_patients_data()
    if pid in data:
        return {"result": data[pid]}    
    raise HTTPException(status_code=404, detail=f"no patient with {pid} exists")

@app.get("/patients")
def view_patients(sort_column:str=Query(...,title="sort column", description="Sort the column", examples=["weight"]), order_by:str=Query(None,title="Order_by", description="Order by 'asc' | 'desc'", examples=["asc"])):
    columnsTBS:list[str]=["height","weight","bmi"] #columnsTBS=columns to be sorted, only accept these columns in the parameter else return 400 Bad Request status code    
    if sort_column not in columnsTBS:
        raise HTTPException(status_code=400, detail=f"Use a valid column name. valid columns={columnsTBS}")
    data=load_patients_data()
    is_desc:bool=True if order_by=="desc" else False    
    sorted_values=sorted(data.values(), key= lambda x: x.get(sort_column,0), reverse=is_desc)
    
    return sorted_values

@app.post("/create_patient")
def create_patient(patient:Patient):
    data=load_patients_data()
    write_data:bool=False
    if patient.id not in data:
        data[patient.id]=patient.model_dump(exclude={"id"})
        write_data:bool=write_patients_data(data)
        if write_data:
            return JSONResponse(content=f"Patient record with {patient.id} created successfully", status_code=201)
    raise HTTPException(status_code=409,detail=f"Patient with {patient.id} already exists")


@app.put("/update_patient/{pid}")
def update_patient_info(updPInfo:UpdatePatient,pid:str=Path(title="PatientId", examples=["P001"], min_length=4)):
    data=load_patients_data()
    if pid not in data:
        raise HTTPException(status_code=404, detail=f"Patient with pid={pid} doesn't exist")
    
    updateInfo=updPInfo.model_dump(exclude_unset=True)
    get_patient_data=data.get(pid,None)    
    
    if get_patient_data:
        for key in updateInfo:
            get_patient_data[key]=updateInfo[key]
        get_patient_data["id"]=pid

    #load the patients data using the Patient model(this is used to calculate the bmi and verdict dynamically)    
    patientModel=Patient.model_validate(get_patient_data)
    data[pid]=patientModel.model_dump(exclude={"id"})

    #write the uopdated patients details to the json file
    write_patients_data(data)

    return JSONResponse(data[pid],status_code=200)

@app.delete("/delete_patient/{pid}")
def delete_patient_info(pid:str=Path(description="Patient ID")):
    data=load_patients_data()
    if pid not in data:
        raise HTTPException(status_code=404, detail=f"Patient with pid={pid} doesn't exist")
    del data[pid]
    write_patients_data(data)
    return Response(status_code=204)





if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=8000, reload=True)
    
