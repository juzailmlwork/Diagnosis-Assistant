from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
import json
import os

app = FastAPI()

# Security setup
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_FILE = "users.json"
CASES_FILE = "clinical_cases.json"

# Initialize data files
for f in [USERS_FILE, CASES_FILE]:
    if not os.path.exists(f):
        with open(f, "w") as file:
            json.dump([], file)

# Helpers
def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_cases():
    with open(CASES_FILE) as f:
        return json.load(f)

def save_cases(cases):
    with open(CASES_FILE, "w") as f:
        json.dump(cases, f, indent=2)

def authenticate_user(username: str, password: str):
    users = load_users()
    for user in users:
        if user["username"] == username and pwd_context.verify(password, user["password"]):
            return user
    return None

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.post("/signup")
def signup(username: str, password: str):
    users = load_users()
    if any(u["username"] == username for u in users):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = pwd_context.hash(password)
    users.append({"username": username, "password": hashed_pw})
    save_users(users)
    return {"msg": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.post("/submit_case")
def submit_case(case: dict, username: str = Depends(get_current_user)):
    cases = load_cases()
    cases.append({
        "submitted_by": username,
        "timestamp": datetime.utcnow().isoformat(),
        "case": case
    })
    save_cases(cases)
    return {"msg": "Case submitted successfully"}