from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Product, Purchase
from schemas import PurchaseRequest
from datetime import date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/purchase")
def make_purchase(data: PurchaseRequest, db: Session = Depends(get_db)):
    # Validate user
    user = db.query(User).filter_by(phone_number=data.phone_number, unique_code=data.unique_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or invalid code")

    # Validate product
    product = db.query(Product).filter_by(id=data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate requested loyalty usage
    if data.use_loyalty_points > user.loyalty_points:
        raise HTTPException(status_code=400, detail="Not enough loyalty points")
    if data.use_loyalty_points > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 loyalty points allowed")

    # Calculate discount
    discount = data.use_loyalty_points * 0.2
    final_price = max(product.price - discount, 0)

    # Update user points
    user.loyalty_points -= data.use_loyalty_points

    # Save purchase
    purchase = Purchase(
        user_id=user.id,
        item_name=product.name,
        amount=final_price,
        purchase_date=date.today()
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return {
        "message": "Purchase successful",
        "original_price": product.price,
        "loyalty_used": data.use_loyalty_points,
        "discount": discount,
        "amount_paid": final_price,
        "remaining_loyalty_points": user.loyalty_points
    }

@router.get("/stats/total-sales")
def get_total_sales(db: Session = Depends(get_db)):
    total_sales = db.query(Purchase).count()
    return {
        "total_sales": total_sales
    }

@router.get("/stats/total-sales/{store_id}")
def get_total_sales_by_store(store_id: int, db: Session = Depends(get_db)):
    total_sales = db.query(Purchase).filter(Purchase.store_id == store_id).count()
    return {
        "store_id": store_id,
        "total_sales": total_sales
    }

@router.get("/stats/total-orders")
def get_total_orders(db: Session = Depends(get_db)):
    total_orders = db.query(Purchase).count()
    return {
        "total_orders": total_orders
    }
    