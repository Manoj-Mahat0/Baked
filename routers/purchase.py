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
def make_combined_purchase(data: PurchaseRequest, db: Session = Depends(get_db)):
    # Validate user
    user = db.query(User).filter_by(phone_number=data.phone_number, unique_code=data.unique_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or invalid code")

    # If no points sent, treat as 0
    loyalty_to_use = data.use_loyalty_points or 0

    # Validate loyalty usage
    if loyalty_to_use > user.loyalty_points:
        raise HTTPException(status_code=400, detail="Not enough loyalty points")
    if loyalty_to_use > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 loyalty points allowed")

    # Fetch all products
    total_original_price = 0
    purchase_details = []

    for item in data.items:
        product = db.query(Product).filter_by(id=item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        
        total_original_price += product.price
        purchase_details.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price
        })

    # Calculate discount
    discount = loyalty_to_use * 0.2
    final_price = max(total_original_price - discount, 0)

    # Update user loyalty points
    user.loyalty_points -= loyalty_to_use

    # Save purchases
    for detail in purchase_details:
        purchase = Purchase(
            user_id=user.id,
            item_name=detail["product_name"],
            amount=detail["price"],  # you can improve this later
            purchase_date=date.today()
        )
        db.add(purchase)

    db.commit()

    return {
        "message": "Purchase successful",
        "total_original_price": total_original_price,
        "loyalty_used": loyalty_to_use,
        "discount": discount,
        "final_amount_paid": final_price,
        "remaining_loyalty_points": user.loyalty_points,
        "products": purchase_details
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
    