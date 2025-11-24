from sqlmodel import select
from models import User, Mechanic, ServiceRequest
from db import get_session
from typing import Optional, List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_user(name: str, phone: str, role: str, password: Optional[str] = None) -> User:
    with get_session() as session:
        hashed = hash_password(password) if password else None
        user = User(name=name, phone=phone, role=role, password_hash=hashed)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def authenticate_user(phone: str, password: str) -> Optional[User]:
    with get_session() as session:
        user = session.exec(select(User).where(User.phone == phone)).first()
        if not user or not user.password_hash:
            return None
        if verify_password(password, user.password_hash):
            return user
        return None

def get_user_by_phone(phone: str) -> Optional[User]:
    with get_session() as session:
        return session.exec(select(User).where(User.phone == phone)).first()

def create_mechanic(user_id: int, skills: Optional[str] = None) -> Mechanic:
    with get_session() as session:
        mech = Mechanic(user_id=user_id, skills=skills)
        session.add(mech)
        session.commit()
        session.refresh(mech)
        return mech

def update_mechanic_location(mech_id: int, lat: float, lon: float, available: bool = True):
    with get_session() as session:
        mech = session.get(Mechanic, mech_id)
        if not mech:
            return None
        mech.latitude = lat
        mech.longitude = lon
        mech.available = available
        session.add(mech)
        session.commit()
        session.refresh(mech)
        return mech

def list_available_mechanics() -> List[Mechanic]:
    with get_session() as session:
        return session.exec(select(Mechanic).where(Mechanic.available == True)).all()

def create_service_request(customer_id: int, desc: str, cust_lat: float, cust_lon: float) -> ServiceRequest:
    with get_session() as session:
        req = ServiceRequest(
            customer_id=customer_id,
            description=desc,
            cust_lat=cust_lat,
            cust_lon=cust_lon
        )
        session.add(req)
        session.commit()
        session.refresh(req)
        return req

def assign_mechanic_to_request(request_id: int, mechanic_id: int):
    with get_session() as session:
        req = session.get(ServiceRequest, request_id)
        if not req:
            return None
        req.mechanic_id = mechanic_id
        req.status = "accepted"
        session.add(req)
        session.commit()
        session.refresh(req)
        return req

def get_pending_requests() -> List[ServiceRequest]:
    with get_session() as session:
        return session.exec(select(ServiceRequest).where(ServiceRequest.status == "pending")).all()
