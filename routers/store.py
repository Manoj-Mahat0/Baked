from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Store, User
from schemas import StoreCreate, UserCreate
from utils.code_utils import generate_unique_4digit

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/store/create")
def create_store(store: StoreCreate, db: Session = Depends(get_db)):
    db_store = Store(**store.dict())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@router.post("/add-user")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    unique_code = generate_unique_4digit(db)
    
    db_user = User(
        full_name=user.full_name,
        phone_number=user.phone_number,
        dob=user.dob,
        store_id=user.store_id,
        loyalty_points=50,
        unique_code=unique_code
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "message": "User created successfully",
        "user_id": db_user.id,
        "unique_code": db_user.unique_code,
        "loyalty_points": db_user.loyalty_points
    }