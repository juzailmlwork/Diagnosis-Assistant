from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import uuid4
from utils import get_final_diagnosis,info_extract
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# ------------------------
# In-memory storage
# ------------------------

users = {}
cases = {} 
next_case_id = 1  # auto-incrementing case ID

# ------------------------
# Data models
# ------------------------s

class Case(BaseModel):
    id: Union[int, str]  # case ID, int internally, can be returned as int or str
    user_id: str
    name: str
    age: int
    sex: str
    chief_complaint: str
    previous_medical_history: Optional[str] = None
    physical_examination:Optional[str] = None
    imageological_examination: Optional[str] = None
    laboratory_examination: Optional[str] = None
    pathological_examination: Optional[str] = None
    differential_diagnosis: List[str]
    final_diagnosis: Optional[str] = None
    reasoning: Optional[str] = None

class CaseCreate(BaseModel):
    user_id: str
    name: str
    age: int
    sex: str
    chief_complaint: str
    previous_medical_history: Optional[str] = None
    physical_examination:Optional[str] = None
    imageological_examination: Optional[str] = None
    laboratory_examination: Optional[str] = None
    pathological_examination: Optional[str] = None
    differential_diagnosis: List[str]

class FinalDiagnosisResponse(BaseModel):
    case_id: Optional[int] = None
    final_diagnosis: Optional[str] = None
    reasoning: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str
    action: str  # "login" or "register"

# class PDFUploadResponse(BaseModel):
#     message: str
#     filename: str
#     extracted_text: Optional[str] = None


# ------------------------
# 1. Login / Register
# ------------------------

@app.post("/login")
def login(request: LoginRequest):
    if request.action == "login":
        # Try to find existing user
        for user in users.values():
            if user["email"] == request.email and user["password"] == request.password:
                return {"user_id": user["id"], "message": "Login successful"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    elif request.action == "register":
        # Check if user already exists
        for user in users.values():
            if user["email"] == request.email:
                raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        new_user = {"id": str(uuid4()), "email": request.email, "password": request.password}
        users[new_user["id"]] = new_user
        return {"user_id": new_user["id"], "message": "Registration successful"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'login' or 'register'")

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
            if str(c.id) == query or c.name.lower() == query.lower():
                results.append(c)
    return results

# ------------------------
# 5. Upload new case — requires user ID
# ------------------------

from fastapi import Query

@app.post("/case", response_model=FinalDiagnosisResponse)
def upload_case(case: CaseCreate):
    global next_case_id
    if case.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    new_case = Case(
        id=next_case_id,
        user_id=case.user_id,
        name=case.name,
        sex=case.sex,
        age=case.age,
        chief_complaint=case.chief_complaint,
        previous_medical_history=case.previous_medical_history,
        imageological_examination=case.imageological_examination,
        laboratory_examination=case.laboratory_examination,
        pathological_examination=case.pathological_examination,
        differential_diagnosis=case.differential_diagnosis,
    )
    differential_diagnosis=new_case.differential_diagnosis
    final_diagnosis,reasoning=get_final_diagnosis(new_case.dict(),differential_diagnosis)
    new_case.final_diagnosis=final_diagnosis
    new_case.reasoning=reasoning
    cases[next_case_id] = new_case
    next_case_id += 1
    
    return FinalDiagnosisResponse(
        case_id= next_case_id-1,
        final_diagnosis=final_diagnosis,
        reasoning=reasoning
    )


# ------------------------
# 6. Upload PDF
# ------------------------

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        contents = await file.read()
        file_path = f"./uploads/{file.filename}"
        
        # Create uploads directory if it doesn't exist
        import os
        os.makedirs("./uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        extracted_information=info_extract(file_path)
        # For now, return basic success response
        # In the future, you can add PDF text extraction here
        return extracted_information
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


