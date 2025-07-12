from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import uuid4

app = FastAPI()

# ------------------------
# In-memory storage
# ------------------------

users = {}  # {user_id (str): User}
cases = {}  # {case_id (int): Case}
next_case_id = 1  # auto-incrementing case ID

# ------------------------
# Data models
# ------------------------

class User(BaseModel):
    id: str
    username: str
    password: str

class Case(BaseModel):
    id: Union[int, str]  # case ID, int internally, can be returned as int or str
    user_id: str
    patient_name: str
    age: int
    chief_complaint: str
    previous_medical_history: Optional[str] = None
    imageological_examination: Optional[str] = None
    laboratory_examination: Optional[str] = None
    pathological_examination: Optional[str] = None
    differential_diagnosis: List[str]
    final_diagnosis: Optional[str] = None
    reasoning: Optional[str] = None

class CaseCreate(BaseModel):
    user_id: str
    patient_name: str
    age: int
    chief_complaint: str
    previous_medical_history: Optional[str] = None
    imageological_examination: Optional[str] = None
    laboratory_examination: Optional[str] = None
    pathological_examination: Optional[str] = None
    differential_diagnosis: List[str]

class FinalDiagnosisResponse(BaseModel):
    status: str  # pending/completed
    final_diagnosis: Optional[str] = None
    reasoning: Optional[str] = None


# ------------------------
# 1. Login / Register
# ------------------------

@app.post("/login", response_model=User)
def login(username: str, password: str):
    for user in users.values():
        if user.username == username and user.password == password:
            return user
    new_user = User(id=str(uuid4()), username=username, password=password)
    users[new_user.id] = new_user
    return new_user

# ------------------------
# 2. Get all cases for user
# ------------------------

@app.get("/cases/{user_id}", response_model=List[Case])
def get_cases(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user_cases = [c for c in cases.values() if c.user_id == user_id]
    return user_cases

# ------------------------
# 3. Get case by ID (case_id is int)
# ------------------------

@app.get("/case/{case_id}", response_model=Case)
def get_case(case_id: int):
    case = cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

# ------------------------
# 4. Search case by ID or patient name — requires user ID
# ------------------------

@app.get("/search", response_model=List[Case])
def search_case(
    user_id: str = Query(...),
    query: str = Query(...)
):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    results = []
    for c in cases.values():
        if c.user_id == user_id:
            if str(c.id) == query or c.patient_name.lower() == query.lower():
                results.append(c)
    return results

# ------------------------
# 5. Upload new case — requires user ID
# ------------------------

from fastapi import Query

@app.post("/case", response_model=Case)
def upload_case(case: CaseCreate, user_id: str = Query(...)):
    global next_case_id
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    new_case = Case(
        id=next_case_id,
        user_id=user_id,
        patient_name=case.patient_name,
        age=case.age,
        chief_complaint=case.chief_complaint,
        previous_medical_history=case.previous_medical_history,
        imageological_examination=case.imageological_examination,
        laboratory_examination=case.laboratory_examination,
        pathological_examination=case.pathological_examination,
        differential_diagnosis=case.differential_diagnosis,
        final_diagnosis=None,
        reasoning=None
    )
    cases[next_case_id] = new_case
    next_case_id += 1
    return new_case


# ------------------------
# 6. Upload PDF
# ------------------------

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    file_path = f"./{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "message": "PDF uploaded successfully"}



# ------------------------
# 7. Get final diagnosis status for a case
# ------------------------

@app.get("/case/{case_id}/final", response_model=FinalDiagnosisResponse)
def get_final_diagnosis(case_id: int):
    case = cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    status = "completed" if case.final_diagnosis else "pending"
    return FinalDiagnosisResponse(
        status=status,
        final_diagnosis=case.final_diagnosis,
        reasoning=case.reasoning
    )

