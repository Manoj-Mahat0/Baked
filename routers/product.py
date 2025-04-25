from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Category, Product
from schemas import CategoryCreate, ProductCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/category/add")
def add_category(category: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(Category).filter_by(name=category.name, store_id=category.store_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists for this store")

    new_cat = Category(**category.dict())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.post("/product/add")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter_by(id=product.category_id, store_id=product.store_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found in this store")

    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products/{store_id}")
def get_products_by_store(store_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter_by(store_id=store_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category.name if p.category else None
        }
        for p in products
    ]
