from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Store, User
from schemas import UserLogin
from utils.jwt_utils import create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def unified_login(payload: UserLogin, db: Session = Depends(get_db)):
    # Try Store login
    store = db.query(Store).filter_by(
        phone_number=payload.phone_number,
        dob=payload.dob
    ).first()
    
    if store:
        role = "MAIN_STORE" if store.mainstore_id is None else "SUB_STORE"
        token = create_access_token({"id": store.id, "role": role})
        return {
            "message": "Login successful",
            "token": token,
            "role": role,
            "store_id": store.id,
            "store_name": store.name
        }

    # Try User login
    user = db.query(User).filter_by(
        phone_number=payload.phone_number,
        dob=payload.dob
    ).first()
    
    if user:
        token = create_access_token({"id": user.id, "role": "USER"})
        return {
            "message": "Login successful",
            "token": token,
            "role": "USER",
            "user_id": user.id,
            "user_name": user.full_name
        }

    # If neither match
    raise HTTPException(status_code=401, detail="Invalid credentials")
