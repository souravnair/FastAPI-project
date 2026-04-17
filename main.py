from fastapi import FastAPI, Path, HTTPException, Query
import json
from typing import Any

app = FastAPI()

def load_patients_data() -> dict[str, dict[str, Any]]:
    with open("patients.json", "r", encoding="utf-8") as p:
        patients_data: dict[str, dict[str, Any]] = json.load(p) #if file is open use json.load(file) ==> json.load(p) instead of loading the file separately and loading the string using json.loads()
        # print(patients_data)
        p.close()

    return patients_data

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


if __name__ == "__main__":
    load_patients_data()
    
