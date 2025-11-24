from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str = Field(index=True, unique=True)
    role: str
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Mechanic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    skills: Optional[str] = None
    available: bool = Field(default=True)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ServiceRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="user.id")
    mechanic_id: Optional[int] = Field(default=None, foreign_key="mechanic.id")
    description: Optional[str] = None
    status: str = Field(default="pending")
    cust_lat: Optional[float] = None
    cust_lon: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
