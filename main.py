from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import math
import crud
from typing import Optional
from db import create_db_and_tables
from auth import create_access_token, decode_token

app = FastAPI(title="MechFinder API")
create_db_and_tables()

# Schemas
class RegisterIn(BaseModel):
    name: str
    phone: str
    password: str
    role: str

class TokenIn(BaseModel):
    phone: str
    password: str

class MechanicLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    available: Optional[bool] = True

class ServiceRequestIn(BaseModel):
    description: str
    cust_lat: float
    cust_lon: float

# Utils
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon / 2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Auth dependency
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, "Invalid header")
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(401, "Invalid token")
    phone = payload["sub"]
    user = crud.get_user_by_phone(phone)
    if not user:
        raise HTTPException(401, "User not found")
    return user

# Routes
@app.post("/register")
def register(data: RegisterIn):
    existing = crud.get_user_by_phone(data.phone)
    if existing:
        raise HTTPException(400, "Phone already registered")
    user = crud.create_user(data.name, data.phone, data.role, data.password)
    if data.role == "mechanic":
        mech = crud.create_mechanic(user.id)
        return {"user": user, "mechanic": mech}
    return {"user": user}

@app.post("/token")
def token(data: TokenIn):
    user = crud.authenticate_user(data.phone, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    access_token = create_access_token({"sub": user.phone})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def home():
    return {"status":"MechFinder API is running"}
