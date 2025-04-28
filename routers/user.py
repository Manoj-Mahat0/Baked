from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Purchase, Store, User
from utils.jwt_utils import decode_token, get_user_by_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ 1. Total users count
@router.get("/users/count")
def get_total_users(db: Session = Depends(get_db)):
    total = db.query(User).count()
    return {"total_users": total}

# ✅ 2. Count of users by store ID
@router.get("/users/count/{store_id}")
def get_users_by_store(store_id: int, db: Session = Depends(get_db)):
    count = db.query(User).filter(User.store_id == store_id).count()
    return {"store_id": store_id, "user_count": count}

# ✅ Fetch user info by phone number
@router.get("/user/info/{phone_number}")
def get_user_info(phone_number: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone_number).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    orders = db.query(Purchase).filter(Purchase.user_id == user.id).all()

    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "loyalty_points": user.loyalty_points,
        "unique_code": user.unique_code,
        "orders": [
            {
                "item_name": order.item_name,
                "amount": order.amount,
                "purchase_date": str(order.purchase_date)
            }
            for order in orders
        ]
    }
@router.get("/user/purchases/{phone_number}")
def get_user_purchases(phone_number: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()

    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "loyalty_points": user.loyalty_points,
        "total_redeemed": sum(p.loyalty_used for p in purchases),
        "purchase_history": [
            {
                "item_name": p.item_name,
                "amount_paid": p.amount,
                "loyalty_redeemed": p.loyalty_used,
                "purchase_date": str(p.purchase_date)
            }
            for p in purchases
        ]
    }

@router.get("/user/me")
def get_logged_in_user(token: str, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid Token")

    user_id = payload.get("id")
    role = payload.get("role")

    if user_id is None or role is None:
        raise HTTPException(status_code=401, detail="Invalid token structure")

    if role == "USER":
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user.id,
            "store_id": user.store_id,
            "full_name": user.full_name,
            "role": role
        }

    elif role in ["MAIN_STORE", "SUB_STORE"]:
        store = db.query(Store).filter(Store.id == user_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return {
            "store_id": store.id,
            "store_name": store.name,
            "role": role
        }

    else:
        raise HTTPException(status_code=401, detail="Invalid role")

